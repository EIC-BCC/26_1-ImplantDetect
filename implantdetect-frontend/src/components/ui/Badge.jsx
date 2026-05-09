const colorMap = {
  blue: "bg-blue-100 text-blue-800",
  green: "bg-green-100 text-green-800",
  red: "bg-red-100 text-red-800",
  amber: "bg-amber-100 text-amber-800",
  gray: "bg-gray-100 text-gray-800",
  purple: "bg-purple-100 text-purple-800",
  teal: "bg-teal-100 text-teal-800",
};

const Badge = ({ children, color = "blue", className = "", dot = false }) => {
  return (
    <span
      className={`
      inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
      ${colorMap[color]} ${className}
    `}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full bg-current opacity-60`} />
      )}
      {children}
    </span>
  );
};

export default Badge;
