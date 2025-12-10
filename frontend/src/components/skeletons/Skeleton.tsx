import type { HTMLAttributes } from 'react';

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  /** Width of the skeleton (CSS value) */
  width?: string | number;
  /** Height of the skeleton (CSS value) */
  height?: string | number;
  /** Make the skeleton rounded (for avatars) */
  rounded?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Base Skeleton component with pulse animation
 * Used as a building block for more complex skeleton loaders
 */
export function Skeleton({
  width,
  height,
  rounded = false,
  className = '',
  style,
  ...props
}: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200';
  const roundedClass = rounded ? 'rounded-full' : 'rounded';

  return (
    <div
      className={`${baseClasses} ${roundedClass} ${className}`}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
        ...style,
      }}
      {...props}
    />
  );
}

/**
 * Text skeleton - mimics a line of text
 */
export function SkeletonText({
  lines = 1,
  className = '',
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          height={16}
          className={i === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'}
        />
      ))}
    </div>
  );
}

/**
 * Circle skeleton - for avatars and icons
 */
export function SkeletonCircle({
  size = 40,
  className = '',
}: {
  size?: number;
  className?: string;
}) {
  return (
    <Skeleton
      width={size}
      height={size}
      rounded
      className={className}
    />
  );
}

export default Skeleton;
