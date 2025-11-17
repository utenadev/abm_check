"""Program update functionality with diff detection."""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from abm_check.domain.models import Program, Episode
from abm_check.infrastructure.fetcher import AbemaFetcher
from abm_check.infrastructure.storage import ProgramStorage


@dataclass
class EpisodeDiff:
    """Represents changes detected in episodes."""
    
    new_episodes: List[Episode]
    premium_to_free: List[Episode]


class ProgramUpdater:
    """Handle program updates with diff detection."""

    def __init__(self, fetcher=None, storage=None, data_file=None):
        self.fetcher = fetcher or AbemaFetcher()
        self.storage = storage or ProgramStorage(data_file=data_file)
    
    def update_program(self, program_id: str) -> Optional[EpisodeDiff]:
        """
        Update a single program and detect changes.
        
        Args:
            program_id: Program ID to update
            
        Returns:
            EpisodeDiff if changes detected, None otherwise
        """
        old_program = self.storage.find_program(program_id)
        if not old_program:
            return None
        
        new_program = self.fetcher.fetch_program_info(program_id)
        new_program.fetched_at = old_program.fetched_at
        new_program.updated_at = datetime.now()
        
        diff = self._detect_changes(old_program, new_program)
        
        if diff.new_episodes or diff.premium_to_free:
            self.storage.save_program(new_program)
        
        return diff
    
    def update_all_programs(self) -> dict[str, EpisodeDiff]:
        """
        Update all programs.
        
        Returns:
            Dict mapping program_id to EpisodeDiff for changed programs
        """
        programs = self.storage.load_programs()
        results = {}
        
        for program in programs:
            diff = self.update_program(program.id)
            if diff and (diff.new_episodes or diff.premium_to_free):
                results[program.id] = diff
        
        return results
    
    def _detect_changes(self, old_program: Program, new_program: Program) -> EpisodeDiff:
        """Detect new episodes and premium-to-free changes."""
        old_episodes = {ep.id: ep for ep in old_program.episodes}
        new_episodes_list = []
        premium_to_free_list = []
        
        for new_ep in new_program.episodes:
            old_ep = old_episodes.get(new_ep.id)
            
            if old_ep is None:
                if new_ep.is_downloadable:
                    new_episodes_list.append(new_ep)
            else:
                if old_ep.is_premium_only and new_ep.is_downloadable:
                    premium_to_free_list.append(new_ep)
        
        return EpisodeDiff(
            new_episodes=new_episodes_list,
            premium_to_free=premium_to_free_list
        )
