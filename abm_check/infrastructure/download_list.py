"""Download list generator."""
from pathlib import Path
from typing import List, Optional, Any, Dict
from datetime import datetime
import yaml
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
        output_file: str = "download_urls.txt",
        format: str = "txt"
    ) -> Path:
        """
        Generate download URL list file.
        
        Args:
            program: Program information
            diff: Episode diff with new/changed episodes
            output_file: Output filename
            format: Output format ('txt' or 'yaml')
            
        Returns:
            Path to generated file
        """
        if format == "yaml":
            return self._generate_yaml_list({program.id: (program, diff)}, output_file)
            
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
        output_file: str = "download_urls.txt",
        format: str = "txt"
    ) -> Optional[Path]:
        """
        Generate combined download list for multiple programs.
        
        Args:
            updates: Dict of program_id -> (Program, EpisodeDiff)
            output_file: Output filename
            format: Output format ('txt' or 'yaml')
            
        Returns:
            Path to generated file
        """
        if format == "yaml":
            return self._generate_yaml_list(updates, output_file)

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

    def _generate_yaml_list(
        self,
        updates: dict[str, tuple[Program, EpisodeDiff]],
        output_file: str
    ) -> Path:
        """Generate YAML format download list."""
        entries = []
        total_new = 0
        total_p2f = 0

        for program_id, (program, diff) in updates.items():
            # Process new episodes
            for ep in diff.new_episodes:
                entry = self._create_yaml_entry(ep, program, "new")
                entries.append(entry)
                total_new += 1
            
            # Process premium to free
            for ep in diff.premium_to_free:
                entry = self._create_yaml_entry(ep, program, "premium_to_free")
                entries.append(entry)
                total_p2f += 1
        
        if not entries:
            # Create empty file with metadata even if no entries? 
            # The txt version returns None/empty. Let's return a file with empty entries for consistency or just minimal metadata.
            # But based on typical use case, if nothing to download, maybe we shouldn't fail but just empty entries.
            pass

        data = {
            "entries": entries,
            "metadata": {
                "generated_at": datetime.now().astimezone().isoformat(),
                "abm_check_version": "1.0.0",
                "total_entries": len(entries),
                "new_episodes": total_new,
                "premium_to_free": total_p2f
            }
        }
        
        output_path = self.output_dir / output_file
        
        # Manually add header comments
        header = f"# AsaCast Download List\n# Generated by abm_check at {data['metadata']['generated_at']}\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            
        return output_path

    def _create_yaml_entry(self, ep: Episode, program: Program, entry_type: str) -> Dict[str, Any]:
        """Create a single YAML entry dictionary."""
        return {
            "id": ep.id,
            "url": ep.get_episode_url(program.id),
            "title": ep.title,
            "series": program.title,
            "episode_number": ep.number,
            "season_number": 1,  # TODO: Season support if available in Episode model
            "duration": ep.duration,
            "thumbnail": ep.thumbnail_url,
            "upload_date": ep.upload_date if ep.upload_date else "",
            "platform": program.platform,
            "entry_type": entry_type
        }
