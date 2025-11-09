"""Program storage using YAML."""
import yaml
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.domain.exceptions import StorageError, ProgramNotFoundError
from abm_check.config import get_config


class ProgramStorage:
    """Manage program data in YAML format."""
    
    def __init__(self, data_file: str = None, config=None):
        """
        Initialize storage.
        
        Args:
            data_file: Path to YAML data file (optional)
            config: Configuration object (optional)
        """
        self.config = config or get_config()
        if data_file is None:
            data_file = self.config.programs_file
        self.data_file = Path(data_file)
    
    def save_program(self, program: Program) -> None:
        """
        Save program to YAML file.
        
        Args:
            program: Program to save
            
        Raises:
            StorageError: If save fails
        """
        try:
            programs = self.load_programs()
            
            # Update existing or add new
            existing_index = None
            for i, p in enumerate(programs):
                if p.id == program.id:
                    existing_index = i
                    break
            
            if existing_index is not None:
                programs[existing_index] = program
            else:
                programs.append(program)
            
            # Convert to dict for YAML
            data = {
                'programs': [self._program_to_dict(p) for p in programs],
                'lastUpdated': datetime.now().isoformat()
            }
            
            # Write to file
            with open(self.data_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
                
        except Exception as e:
            raise StorageError("save_program", str(e))
    
    def load_programs(self) -> List[Program]:
        """
        Load all programs from YAML file.
        
        Returns:
            List of Program objects
            
        Raises:
            StorageError: If load fails
        """
        if not self.data_file.exists():
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'programs' not in data:
                return []
            
            return [self._dict_to_program(p) for p in data['programs']]
            
        except yaml.YAMLError as e:
            raise StorageError("load_programs", "YAML parsing error") from e
        except Exception as e:
            raise StorageError("load_programs", str(e))
    
    def find_program(self, program_id: str) -> Optional[Program]:
        """
        Find program by ID.
        
        Args:
            program_id: Program ID to find
            
        Returns:
            Program if found, None otherwise
        """
        programs = self.load_programs()
        for program in programs:
            if program.id == program_id:
                return program
        return None
    
    def delete_program(self, program_id: str) -> None:
        """
        Delete program by ID.
        
        Args:
            program_id: Program ID to delete
            
        Raises:
            ProgramNotFoundError: If program not found
            StorageError: If delete fails
        """
        try:
            programs = self.load_programs()
            
            existing_index = None
            for i, p in enumerate(programs):
                if p.id == program_id:
                    existing_index = i
                    break
            
            if existing_index is None:
                raise ProgramNotFoundError(program_id)
            
            programs.pop(existing_index)
            
            data = {
                'programs': [self._program_to_dict(p) for p in programs],
                'lastUpdated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
                
        except ProgramNotFoundError:
            raise
        except Exception as e:
            raise StorageError("delete_program", str(e))
    
    def get_all_program_ids(self) -> list[str]:
        """
        Get all program IDs.
        
        Returns:
            List of program IDs
        """
        programs = self.load_programs()
        return [p.id for p in programs]
    
    def _program_to_dict(self, program: Program) -> dict:
        """Convert Program to dict for YAML."""
        return {
            'id': program.id,
            'title': program.title,
            'description': program.description,
            'url': program.url,
            'thumbnailUrl': program.thumbnail_url,
            'totalEpisodes': program.total_episodes,
            'latestEpisodeNumber': program.latest_episode_number,
            'fetchedAt': program.fetched_at.isoformat(),
            'updatedAt': program.updated_at.isoformat(),
            'episodes': [self._episode_to_dict(ep) for ep in program.episodes]
        }
    
    def _episode_to_dict(self, episode: Episode) -> dict:
        """Convert Episode to dict for YAML."""
        episode_dict = {
            'id': episode.id,
            'number': episode.number,
            'title': episode.title,
            'description': episode.description,
            'duration': episode.duration,
            'thumbnailUrl': episode.thumbnail_url,
            'isDownloadable': episode.is_downloadable,
            'isPremiumOnly': episode.is_premium_only,
            'downloadUrl': episode.download_url,
            'uploadDate': episode.upload_date,
        }
        
        if episode.formats:
            episode_dict['formats'] = [
                {
                    'formatId': fmt.format_id,
                    'resolution': fmt.resolution,
                    'tbr': fmt.tbr,
                    'url': fmt.url,
                }
                for fmt in episode.formats
            ]
        
        return episode_dict
    
    def _dict_to_program(self, data: dict) -> Program:
        """Convert dict to Program."""
        episodes = [self._dict_to_episode(ep) for ep in data.get('episodes', [])]
        
        return Program(
            id=data['id'],
            title=data['title'],
            description=data.get('description', ''),
            url=data['url'],
            thumbnail_url=data.get('thumbnailUrl', ''),
            total_episodes=data.get('totalEpisodes', 0),
            latest_episode_number=data.get('latestEpisodeNumber', 0),
            episodes=episodes,
            fetched_at=datetime.fromisoformat(data['fetchedAt']),
            updated_at=datetime.fromisoformat(data['updatedAt'])
        )
    
    def _dict_to_episode(self, data: dict) -> Episode:
        """Convert dict to Episode."""
        formats = []
        if 'formats' in data:
            formats = [
                VideoFormat(
                    format_id=fmt.get('formatId', ''),
                    resolution=fmt.get('resolution', ''),
                    tbr=fmt.get('tbr', 0.0),
                    url=fmt.get('url', '')
                )
                for fmt in data['formats']
            ]
        
        return Episode(
            id=data['id'],
            number=data['number'],
            title=data['title'],
            description=data.get('description', ''),
            duration=data.get('duration', 0),
            thumbnail_url=data.get('thumbnailUrl', ''),
            is_downloadable=data.get('isDownloadable', False),
            is_premium_only=data.get('isPremiumOnly', True),
            download_url=data.get('downloadUrl'),
            formats=formats,
            upload_date=data.get('uploadDate')
        )
