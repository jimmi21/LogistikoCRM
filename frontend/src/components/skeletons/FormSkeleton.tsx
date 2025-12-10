import { Skeleton } from './Skeleton';

interface FormSkeletonProps {
  /** Number of fields to display */
  fields?: number;
  /** Show form in grid layout (2 columns) */
  twoColumns?: boolean;
  /** Show submit buttons */
  showButtons?: boolean;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Form skeleton with labels and input fields
 */
export function FormSkeleton({
  fields = 4,
  twoColumns = false,
  showButtons = true,
  className = '',
}: FormSkeletonProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      <div className={twoColumns ? 'grid grid-cols-1 md:grid-cols-2 gap-4' : 'space-y-4'}>
        {Array.from({ length: fields }).map((_, i) => (
          <FormFieldSkeleton key={i} />
        ))}
      </div>

      {showButtons && (
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
          <Skeleton height={40} width={80} />
          <Skeleton height={40} width={120} />
        </div>
      )}
    </div>
  );
}

/**
 * Single form field skeleton (label + input)
 */
export function FormFieldSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse ${className}`}>
      {/* Label */}
      <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
      {/* Input */}
      <div className="h-10 bg-gray-200 rounded w-full" />
    </div>
  );
}

/**
 * Textarea field skeleton
 */
export function TextareaSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse ${className}`}>
      {/* Label */}
      <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
      {/* Textarea */}
      <div className="h-24 bg-gray-200 rounded w-full" />
    </div>
  );
}

/**
 * Select field skeleton
 */
export function SelectSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse ${className}`}>
      {/* Label */}
      <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
      {/* Select */}
      <div className="h-10 bg-gray-200 rounded w-full" />
    </div>
  );
}

/**
 * Checkbox/Radio group skeleton
 */
export function CheckboxGroupSkeleton({
  options = 3,
  className = '',
}: {
  options?: number;
  className?: string;
}) {
  return (
    <div className={`animate-pulse space-y-2 ${className}`}>
      {/* Label */}
      <div className="h-4 bg-gray-200 rounded w-32 mb-3" />
      {/* Options */}
      {Array.from({ length: options }).map((_, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded w-24" />
        </div>
      ))}
    </div>
  );
}

export default FormSkeleton;
