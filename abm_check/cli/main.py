"""Main CLI entry point."""
import click
import sys
import logging
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.markdown import MarkdownGenerator
from abm_check.infrastructure.updater import ProgramUpdater
from abm_check.infrastructure.download_list import DownloadListGenerator
from abm_check.domain.exceptions import AbmCheckError, InvalidProgramIdError
from abm_check.utils.validation import validate_program_id


# Setup logging
def setup_logger(verbose: bool = False, quiet: bool = False) -> logging.Logger:
    """Setup logger for CLI."""
    logger = logging.getLogger('abm_check')
    
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    
    return logger


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='詳細ログ出力')
@click.option('--quiet', '-q', is_flag=True, help='エラーのみ出力')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """ABEMA番組情報管理ツール"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    ctx.obj['logger'] = setup_logger(verbose, quiet)


@cli.command()
@click.argument('program_id_or_url')
@click.pass_context
def add(ctx: click.Context, program_id_or_url: str) -> None:
    """
    番組を追加
    
    PROGRAM_ID_OR_URL: 番組ID (例: 26-249) または URL
    """
    logger = ctx.obj['logger']
    
    try:
        # Extract program ID from URL if needed
        program_id = program_id_or_url
        if 'abema.tv' in program_id_or_url:
            program_id = program_id_or_url.split('/')[-1]
        
        validate_program_id(program_id)
        
        logger.info(f"Fetching program info: {program_id}")
        
        # Fetch program info
        fetcher = AbemaFetcher()
        program = fetcher.fetch_program_info(program_id)
        
        logger.info(f"Program: {program.title}")
        logger.info(f"Episodes: {program.total_episodes}")
        
        # Save to YAML
        storage = ProgramStorage()
        storage.save_program(program)
        logger.info("Saved to: programs.yaml")
        
        # Generate Markdown
        md_gen = MarkdownGenerator()
        md_file = md_gen.save_program_md(program)
        logger.info(f"Markdown: {md_file}")
        
        sys.exit(0)
        
    except AbmCheckError as e:
        logger.error(f"Failed to add program: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list(ctx: click.Context) -> None:
    """番組一覧を表示"""
    logger = ctx.obj['logger']
    
    try:
        storage = ProgramStorage()
        programs = storage.load_programs()
        
        if not programs:
            logger.info("No programs found")
            sys.exit(0)
        
        sorted_programs = sorted(programs, key=lambda p: p.updated_at, reverse=True)
        
        ctx.obj['program_list'] = sorted_programs
        
        for i, program in enumerate(sorted_programs, 1):
            print(f"{i} {program.id} {program.title}")
        
        sys.exit(0)
        
    except AbmCheckError as e:
        logger.error(f"Failed to list programs: {e}")
        sys.exit(1)


@cli.command()
@click.argument('program_id')
@click.pass_context
def view(ctx: click.Context, program_id: str) -> None:
    """
    番組詳細を表示
    
    PROGRAM_ID: 番組IDまたは `list` コマンドで表示されるシーケンス番号
    """
    logger = ctx.obj['logger']
    
    try:
        from pathlib import Path
        
        actual_program_id = program_id
        
        if program_id.isdigit():
            storage = ProgramStorage()
            programs = storage.load_programs()
            sorted_programs = sorted(programs, key=lambda p: p.updated_at, reverse=True)
            
            seq = int(program_id)
            if 1 <= seq <= len(sorted_programs):
                actual_program_id = sorted_programs[seq - 1].id
            else:
                logger.error(f"Invalid seq number: {seq}")
                sys.exit(1)
        
        md_file = Path("output") / actual_program_id / "program.md"
        
        if not md_file.exists():
            logger.error(f"Program not found: {actual_program_id}")
            sys.exit(1)
        
        content = md_file.read_text(encoding='utf-8')
        print(content)
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Failed to view program: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """バージョン情報を表示"""
    import yt_dlp
    
    print("abm_check version 1.0.0")
    print(f"yt-dlp version {yt_dlp.version.__version__}")
    
    sys.exit(0)


@cli.command()
@click.argument('program_id', required=False)
@click.option('--output', '-o', default='download_urls.txt', help='出力ファイル名')
@click.pass_context
def update(ctx: click.Context, program_id: str, output: str) -> None:
    """
    番組情報を更新してDL対象を検出
    
    PROGRAM_ID: 番組ID (省略時は全番組を更新)
    """
    logger = ctx.obj['logger']
    
    try:
        updater = ProgramUpdater()
        dl_gen = DownloadListGenerator()
        storage = ProgramStorage()
        md_gen = MarkdownGenerator()
        
        if program_id:
            logger.info(f"Updating program: {program_id}")
            diff = updater.update_program(program_id)
            
            if not diff:
                logger.error(f"Program not found: {program_id}")
                sys.exit(1)
            
            if not diff.new_episodes and not diff.premium_to_free:
                logger.info("No changes detected")
                sys.exit(0)
            
            program = storage.find_program(program_id)
            md_gen.save_program_md(program)
            
            dl_file = dl_gen.generate_download_list(program, diff, output)
            
            logger.info(f"Changes detected:")
            logger.info(f"  New episodes: {len(diff.new_episodes)}")
            logger.info(f"  Premium to free: {len(diff.premium_to_free)}")
            logger.info(f"Download list: {dl_file}")
            
        else:
            logger.info("Updating all programs...")
            results = updater.update_all_programs()
            
            if not results:
                logger.info("No changes detected in any program")
                sys.exit(0)
            
            updates = {}
            for prog_id, diff in results.items():
                program = storage.find_program(prog_id)
                md_gen.save_program_md(program)
                updates[prog_id] = (program, diff)
            
            dl_file = dl_gen.generate_combined_list(updates, output)
            
            logger.info(f"Updated {len(results)} programs")
            for prog_id, diff in results.items():
                program = storage.find_program(prog_id)
                logger.info(f"  {program.title}:")
                logger.info(f"    New episodes: {len(diff.new_episodes)}")
                logger.info(f"    Premium to free: {len(diff.premium_to_free)}")
            
            if dl_file:
                logger.info(f"Download list: {dl_file}")
        
        sys.exit(0)
        
    except AbmCheckError as e:
        logger.error(f"Failed to update: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli(obj={})
