import type { AdvancedSearchOptions } from '@/types/search';

/**
 * Check if advanced options have any active filters
 */
export function hasActiveFilters(options: AdvancedSearchOptions | null | undefined): boolean {
  if (!options) return false;
  return (
    options.yearFrom !== undefined ||
    options.yearTo !== undefined ||
    options.root.children.length > 0
  );
}

/**
 * Serialize AdvancedSearchOptions to URL-safe string
 * Returns undefined if no active filters (to keep URL clean)
 */
export function serializeAdvancedOptions(options: AdvancedSearchOptions | null | undefined): string | undefined {
  if (!hasActiveFilters(options)) {
    return undefined;
  }
  return encodeURIComponent(JSON.stringify(options));
}

/**
 * Deserialize URL string back to AdvancedSearchOptions
 * Returns null if invalid or empty
 */
export function deserializeAdvancedOptions(encoded: string | null | undefined): AdvancedSearchOptions | null {
  if (!encoded) return null;

  try {
    const decoded = decodeURIComponent(encoded);
    const parsed = JSON.parse(decoded) as AdvancedSearchOptions;

    // Validate structure
    if (typeof parsed !== 'object' || !parsed.root) {
      return null;
    }

    return parsed;
  } catch {
    return null;
  }
}
