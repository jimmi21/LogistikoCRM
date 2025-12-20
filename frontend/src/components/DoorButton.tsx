import { useState } from 'react';
import { DoorOpen, Loader2, WifiOff, Check, EyeOff } from 'lucide-react';
import { useOpenDoor, useDoorStatus } from '../hooks/useDoor';

export default function DoorButton() {
  const { data: status, isLoading: isCheckingStatus } = useDoorStatus();
  const openDoor = useOpenDoor();
  const [showSuccess, setShowSuccess] = useState(false);

  const handleClick = async () => {
    try {
      // Toggle mode - ON/OFF with single click
      await openDoor.mutateAsync();
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 2000);
    } catch {
      // Error is handled by the mutation
    }
  };

  // Check if door control is disabled in settings
  const isDisabled = status?.enabled === false;
  const isOffline = status && !status.online && !isDisabled;
  const isLoading = openDoor.isPending || isCheckingStatus;

  // Don't render button if disabled in settings
  if (isDisabled) {
    return null;
  }

  // Determine button state and styling
  let buttonStyle = 'bg-blue-600 hover:bg-blue-700 text-white';
  let icon = <DoorOpen size={18} />;
  let label = status?.device_name || 'Πόρτα';

  if (isOffline) {
    buttonStyle = 'bg-gray-400 text-white cursor-not-allowed';
    icon = <WifiOff size={18} />;
    label = 'Offline';
  } else if (showSuccess) {
    buttonStyle = 'bg-green-500 text-white';
    icon = <Check size={18} />;
    label = 'OK!';
  } else if (isLoading) {
    buttonStyle = 'bg-blue-500 text-white opacity-70 cursor-wait';
    icon = <Loader2 size={18} className="animate-spin" />;
    label = '...';
  } else if (openDoor.isError) {
    buttonStyle = 'bg-red-500 hover:bg-red-600 text-white';
  }

  return (
    <button
      onClick={handleClick}
      disabled={isLoading || isOffline}
      className={`
        flex items-center gap-2 px-3 py-2 rounded-lg font-medium text-sm
        transition-all duration-200
        ${buttonStyle}
        ${isLoading || isOffline ? '' : 'active:scale-95'}
      `}
      title={isOffline ? 'Η συσκευή είναι offline' : 'Toggle πόρτας (ON/OFF)'}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}
