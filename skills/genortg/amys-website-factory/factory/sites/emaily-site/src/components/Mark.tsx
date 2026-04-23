export function Mark({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      width="28"
      height="28"
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M6 8.75C6 7.231 7.231 6 8.75 6h10.5C20.769 6 22 7.231 22 8.75v10.5C22 20.769 20.769 22 19.25 22H8.75C7.231 22 6 20.769 6 19.25V8.75Z"
        stroke="currentColor"
        strokeOpacity="0.85"
        strokeWidth="1.4"
      />
      <path
        d="M8.25 9.3h11.5v.2c0 2.75-2.2 5.0-4.95 5.05H13.2C10.45 14.5 8.25 12.3 8.25 9.55v-.25Z"
        fill="currentColor"
        fillOpacity="0.14"
      />
      <path
        d="M8.6 10.2l4.85 3.55c.33.24.78.24 1.1 0l4.85-3.55"
        stroke="currentColor"
        strokeOpacity="0.7"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9.4 18.9h9.2"
        stroke="currentColor"
        strokeOpacity="0.65"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
      <path
        d="M9.4 16.4h6.2"
        stroke="currentColor"
        strokeOpacity="0.65"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
    </svg>
  );
}

