/**
 * Base path utilities for DataRobot Custom Application deployment.
 *
 * DataRobot serves custom applications at subpaths like:
 * https://app.datarobot.com/custom_applications/{app_id}/
 *
 * This module provides utilities to construct correct URLs for both
 * local development and DataRobot deployment.
 */

/**
 * Get the base path for the application.
 *
 * In development: Returns '' (empty string)
 * On DataRobot: Returns '/custom_applications/{app_id}'
 */
export function getBasePath(): string {
  if (typeof window !== 'undefined') {
    const pathname = window.location.pathname;

    // Detect DataRobot custom application path
    const drMatch = pathname.match(/^(\/custom_applications\/[^/]+)/);
    if (drMatch) {
      return drMatch[1];
    }
  }
  return '';
}

/**
 * Construct a full path for assets or API endpoints.
 *
 * @param path - The path to append (should start with '/')
 * @returns The full path including base path
 *
 * @example
 * // In development: '/api/v1/config'
 * // On DataRobot: '/custom_applications/abc123/api/v1/config'
 * assetPath('/api/v1/config')
 */
export function assetPath(path: string): string {
  const base = getBasePath();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}

/**
 * Construct a URL for API calls.
 * Alias for assetPath with clearer intent.
 */
export function apiUrl(endpoint: string): string {
  return assetPath(endpoint);
}
