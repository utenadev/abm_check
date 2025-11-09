"""Download list generator."""
from pathlib import Path
from typing import List
from abm_check.domain.models import Program, Episode
from abm_check.infrastructure.updater import EpisodeDiff


class DownloadListGenerator:
    """Generate download URL list files."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_download_list(
        self,
        program: Program,
        diff: EpisodeDiff,
        output_file: str = "download_urls.txt"
    ) -> Path:
        """
        Generate download URL list file.
        
        Args:
            program: Program information
            diff: Episode diff with new/changed episodes
            output_file: Output filename
            
        Returns:
            Path to generated file
        """
        lines = []
        
        if diff.new_episodes:
            lines.append(f"# {program.title} - New Episodes")
            for ep in sorted(diff.new_episodes, key=lambda x: x.number):
                url = ep.get_episode_url(program.id)
                lines.append(f"# Episode {ep.number}: {ep.title}")
                lines.append(url)
                lines.append("")
        
        if diff.premium_to_free:
            lines.append(f"# {program.title} - Premium to Free")
            for ep in sorted(diff.premium_to_free, key=lambda x: x.number):
                url = ep.get_episode_url(program.id)
                lines.append(url)
            lines.append("")
        
        output_path = self.output_dir / output_file
        output_path.write_text("\n".join(lines), encoding="utf-8")
        
        return output_path
    
    def generate_combined_list(
        self,
        updates: dict[str, tuple[Program, EpisodeDiff]],
        output_file: str = "download_urls.txt"
    ) -> Path:
        """
        Generate combined download list for multiple programs.
        
        Args:
            updates: Dict of program_id -> (Program, EpisodeDiff)
            output_file: Output filename
            
        Returns:
            Path to generated file
        """
        lines = []
        
        for program_id, (program, diff) in updates.items():
            if diff.new_episodes:
                lines.append(f"# {program.title} - New Episodes")
                for ep in sorted(diff.new_episodes, key=lambda x: x.number):
                    url = ep.get_episode_url(program.id)
                    lines.append(f"# Episode {ep.number}: {ep.title}")
                    lines.append(url)
                    lines.append("")
            
            if diff.premium_to_free:
                lines.append(f"# {program.title} - Premium to Free")
                for ep in sorted(diff.premium_to_free, key=lambda x: x.number):
                    url = ep.get_episode_url(program.id)
                    lines.append(url)
                lines.append("")
        
        if not lines:
            return None
        
        output_path = self.output_dir / output_file
        output_path.write_text("\n".join(lines), encoding="utf-8")
        
        return output_path
