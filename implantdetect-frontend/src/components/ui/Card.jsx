const Card = ({
  children,
  className = "",
  hover = false,
  padding = true,
  ...props
}) => {
  return (
    <div
      className={`
        bg-white rounded-xl shadow-sm border border-gray-100
        ${hover ? "hover:shadow-md hover:-translate-y-0.5 transition-all duration-300" : ""}
        ${padding ? "p-6" : ""}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = "" }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-lg font-semibold text-gray-900 ${className}`}>
    {children}
  </h3>
);

const CardDescription = ({ children, className = "" }) => (
  <p className={`text-sm text-gray-500 mt-1 ${className}`}>{children}</p>
);

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;

export default Card;
