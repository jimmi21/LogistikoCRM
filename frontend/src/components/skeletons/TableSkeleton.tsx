import { Skeleton, SkeletonCircle } from './Skeleton';

interface TableSkeletonProps {
  /** Number of rows to display */
  rows?: number;
  /** Number of columns */
  columns?: number;
  /** Show avatar in first column (like Clients table) */
  showAvatar?: boolean;
  /** Show checkbox column */
  showCheckbox?: boolean;
  /** Additional CSS classes for the container */
  className?: string;
}

/**
 * Table skeleton for data tables
 * Mimics the loading state of tables like Clients and Obligations
 */
export function TableSkeleton({
  rows = 5,
  columns = 5,
  showAvatar = false,
  showCheckbox = false,
  className = '',
}: TableSkeletonProps) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Header skeleton */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <Skeleton height={16} width={200} />
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          {/* Table Header */}
          <thead className="bg-gray-50">
            <tr>
              {showCheckbox && (
                <th className="px-4 py-3">
                  <Skeleton width={20} height={20} />
                </th>
              )}
              {Array.from({ length: columns }).map((_, i) => (
                <th key={i} className="px-6 py-3">
                  <Skeleton height={12} width={i === 0 ? 80 : 60} />
                </th>
              ))}
            </tr>
          </thead>

          {/* Table Body */}
          <tbody className="bg-white divide-y divide-gray-200">
            {Array.from({ length: rows }).map((_, rowIndex) => (
              <tr key={rowIndex}>
                {showCheckbox && (
                  <td className="px-4 py-4">
                    <Skeleton width={20} height={20} />
                  </td>
                )}
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <td key={colIndex} className="px-6 py-4 whitespace-nowrap">
                    {colIndex === 0 && showAvatar ? (
                      <div className="flex items-center">
                        <SkeletonCircle size={40} />
                        <div className="ml-4 space-y-2">
                          <Skeleton height={14} width={120} />
                          <Skeleton height={10} width={80} />
                        </div>
                      </div>
                    ) : colIndex === columns - 1 ? (
                      // Actions column
                      <div className="flex justify-end gap-2">
                        <Skeleton width={28} height={28} />
                        <Skeleton width={28} height={28} />
                        <Skeleton width={28} height={28} />
                      </div>
                    ) : (
                      <Skeleton height={14} width={80 + Math.random() * 40} />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/**
 * Simpler inline table rows skeleton (for use inside existing table containers)
 */
export function TableRowsSkeleton({
  rows = 5,
  columns = 5,
  showCheckbox = false,
}: {
  rows?: number;
  columns?: number;
  showCheckbox?: boolean;
}) {
  return (
    <>
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <tr key={rowIndex} className="animate-pulse">
          {showCheckbox && (
            <td className="px-4 py-4">
              <div className="w-5 h-5 bg-gray-200 rounded" />
            </td>
          )}
          {Array.from({ length: columns }).map((_, colIndex) => (
            <td key={colIndex} className="px-6 py-4">
              <div
                className="h-4 bg-gray-200 rounded"
                style={{ width: `${60 + Math.random() * 40}%` }}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}

export default TableSkeleton;
