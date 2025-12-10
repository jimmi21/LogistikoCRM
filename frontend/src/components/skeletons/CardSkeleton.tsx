import { Skeleton, SkeletonText } from './Skeleton';

interface CardSkeletonProps {
  /** Show header section */
  showHeader?: boolean;
  /** Show footer section */
  showFooter?: boolean;
  /** Number of content lines */
  contentLines?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Card skeleton for general card layouts
 */
export function CardSkeleton({
  showHeader = true,
  showFooter = false,
  contentLines = 3,
  className = '',
}: CardSkeletonProps) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      {showHeader && (
        <div className="px-6 py-4 border-b border-gray-200">
          <Skeleton height={20} width={180} />
        </div>
      )}

      <div className="p-6">
        <SkeletonText lines={contentLines} />
      </div>

      {showFooter && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-end gap-3">
            <Skeleton height={36} width={80} />
            <Skeleton height={36} width={100} />
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Grid of card skeletons
 */
export function CardGridSkeleton({
  count = 4,
  columns = 2,
  className = '',
}: {
  count?: number;
  columns?: 2 | 3 | 4;
  className?: string;
}) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} contentLines={2} />
      ))}
    </div>
  );
}

/**
 * List item skeleton for lists within cards
 */
export function ListItemSkeleton({
  count = 5,
  showIcon = false,
  className = '',
}: {
  count?: number;
  showIcon?: boolean;
  className?: string;
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-2 animate-pulse">
          {showIcon && (
            <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0" />
          )}
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
          <div className="h-3 bg-gray-200 rounded w-16" />
        </div>
      ))}
    </div>
  );
}

export default CardSkeleton;
