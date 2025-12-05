import { useQuery } from '@tanstack/react-query';
import { searchApi, type SearchResultItem, type GlobalSearchResponse } from '../api/client';

export interface SearchResults {
  clients: SearchResultItem[];
  obligations: SearchResultItem[];
  tickets: SearchResultItem[];
  calls: SearchResultItem[];
  total: number;
}

const SEARCH_KEY = 'global-search';

/**
 * Hook for global search across all entities.
 * Searches clients, obligations, tickets, and calls.
 *
 * @param query - Search query string
 * @param enabled - Whether to enable the search (typically when modal is open)
 * @returns React Query result with search results grouped by type
 */
export function useGlobalSearch(query: string, enabled: boolean = true) {
  return useQuery<GlobalSearchResponse>({
    queryKey: [SEARCH_KEY, query],
    queryFn: () => searchApi.globalSearch(query),
    enabled: enabled && query.length >= 2, // Minimum 2 characters
    staleTime: 30000, // 30 seconds
    gcTime: 60000, // 1 minute (was cacheTime in v4)
    refetchOnWindowFocus: false,
    retry: 1,
  });
}

export type { SearchResultItem, GlobalSearchResponse };
