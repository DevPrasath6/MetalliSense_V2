import React from "react";
import clsx from "clsx";

const Badge = ({ children, variant = "default", size = "md", className = "" }) => {
  const variants = {
    default: "bg-metal-100 text-metal-700 border-metal-300",
    success: "bg-primary-100 text-primary-700 border-primary-300 shadow-sm shadow-primary-500/20",
    warning: "bg-yellow-100 text-yellow-700 border-yellow-300",
    error: "bg-red-100 text-red-700 border-red-300",
    info: "bg-blue-100 text-blue-700 border-blue-300",
    primary: "bg-gradient-metal text-white border-primary-500 shadow-metal",
  };

  const sizes = {
    sm: "px-1.5 sm:px-2 py-0.5 text-[10px] sm:text-xs",
    md: "px-2 sm:px-3 py-0.5 sm:py-1 text-[10px] sm:text-xs",
    lg: "px-3 sm:px-4 py-1 sm:py-1.5 text-xs sm:text-sm",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full font-semibold border",
        sizes[size],
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
