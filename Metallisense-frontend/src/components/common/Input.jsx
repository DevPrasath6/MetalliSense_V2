import React from "react";
import clsx from "clsx";

const Input = ({
  label,
  error,
  helpText,
  type = "text",
  className = "",
  containerClassName = "",
  ...props
}) => {
  return (
    <div className={clsx("mb-3 sm:mb-4", containerClassName)}>
      {label && (
        <label className="block text-xs sm:text-sm font-semibold text-metal-800 mb-1 sm:mb-2">
          {label}
        </label>
      )}
      <input
        type={type}
        className={clsx(
          "w-full px-3 sm:px-4 py-2 sm:py-2.5 text-sm border-2 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all placeholder:text-metal-400",
          error ? "border-red-500 focus:ring-red-500" : "border-metal-200",
          className
        )}
        {...props}
      />
      {helpText && !error && (
        <p className="mt-1 text-xs text-metal-500">{helpText}</p>
      )}
      {error && <p className="mt-1 sm:mt-1.5 text-xs sm:text-sm text-red-600 font-medium">{error}</p>}
    </div>
  );
};

export default Input;
