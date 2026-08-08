import React, { useEffect } from "react";
import { X } from "lucide-react";
import clsx from "clsx";

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  showClose = true,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizes = {
    sm: "max-w-sm sm:max-w-md",
    md: "max-w-md sm:max-w-xl md:max-w-2xl",
    lg: "max-w-lg sm:max-w-2xl md:max-w-4xl",
    xl: "max-w-xl sm:max-w-3xl md:max-w-5xl lg:max-w-6xl",
    "2xl": "max-w-2xl sm:max-w-4xl md:max-w-5xl lg:max-w-6xl",
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-metal-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-2 sm:p-4">
        <div
          className={clsx(
            "relative bg-white rounded-xl sm:rounded-2xl shadow-metal-xl border border-metal-200 w-full transform transition-all max-h-[90vh] overflow-y-auto",
            sizes[size]
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          {title && (
            <div className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b border-metal-200 bg-gradient-to-r from-metal-50 to-transparent sticky top-0 z-10 bg-white">
              <div className="flex items-center gap-2">
                <div className="w-1 h-5 sm:h-6 bg-gradient-metal rounded-full" />
                <h3 className="text-base sm:text-lg font-bold text-metal-900 truncate">{title}</h3>
              </div>
              {showClose && (
                <button
                  onClick={onClose}
                  className="text-metal-400 hover:text-metal-600 hover:bg-metal-100 p-1.5 sm:p-2 rounded-lg transition-all flex-shrink-0"
                >
                  <X size={18} className="sm:w-5 sm:h-5" />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className="px-4 sm:px-6 py-3 sm:py-4">{children}</div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
