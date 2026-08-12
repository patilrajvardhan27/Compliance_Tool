"use client";

export function Section({
  title,
  hint,
  children,
  className = "",
}: {
  title: string;
  hint?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-lg border border-slate-200 bg-white p-5 shadow-[0_1px_2px_rgba(20,30,45,0.05)] dark:border-slate-800 dark:bg-slate-900 ${className}`}
    >
      <header className="mb-4 border-b border-slate-100 pb-2.5 dark:border-slate-800">
        <h2 className="text-[13px] font-semibold uppercase tracking-[0.08em] text-slate-700 dark:text-slate-200">
          {title}
        </h2>
        {hint && <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{hint}</p>}
      </header>
      <div className="flex flex-col gap-3">{children}</div>
    </section>
  );
}

export function FieldRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  // The whole row is a <label> so the text is announced for (and click-focuses) the control
  // inside it without needing explicit id/htmlFor pairs.
  return (
    <label className="grid grid-cols-[minmax(160px,220px)_1fr] items-center gap-3">
      <span className="text-sm text-slate-600 dark:text-slate-300">{label}</span>
      <div>{children}</div>
    </label>
  );
}

const inputClass =
  "w-full rounded-md border bg-white px-2.5 py-1.5 text-sm text-slate-900 shadow-sm transition-colors focus:border-[var(--cobalt)] focus:outline-none focus:ring-1 focus:ring-[var(--cobalt)] disabled:bg-slate-100 disabled:text-slate-500 dark:bg-slate-800 dark:text-slate-100 dark:disabled:bg-slate-800/60";

/** Empty required-style fields get a quiet amber cast: enter a value, nothing is assumed. */
const filledBorder = "border-slate-300 dark:border-slate-600";
const blankBorder =
  "border-amber-400/70 bg-amber-50/40 dark:border-amber-500/50 dark:bg-amber-950/20";

export function TextInput({
  required,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  // The amber "enter a value" cast only applies to required fields left blank.
  const blank = required && props.value === "" && !props.disabled && !props.readOnly;
  return (
    <input
      {...props}
      className={`${inputClass} ${blank ? blankBorder : filledBorder} ${props.className ?? ""}`}
    />
  );
}

export function NumberInput({
  value,
  onChange,
  ...rest
}: Omit<React.InputHTMLAttributes<HTMLInputElement>, "value" | "onChange"> & {
  /** null = the user has not entered a value; rendered as an empty box, never a default. */
  value: number | null;
  onChange: (value: number | null) => void;
}) {
  const blank = value === null && !rest.disabled && !rest.readOnly;
  return (
    <input
      {...rest}
      type="number"
      inputMode="decimal"
      value={value === null || !Number.isFinite(value) ? "" : value}
      onChange={(e) => {
        const n = e.target.valueAsNumber;
        onChange(Number.isFinite(n) ? n : null);
      }}
      className={`${inputClass} font-mono ${blank ? blankBorder : filledBorder} ${rest.className ?? ""}`}
    />
  );
}

export function SelectField({
  value,
  onChange,
  options,
  placeholder = "Select…",
  createOption,
  onCreate,
  className = "",
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  /** Shown while no option has been chosen; not a selectable value. */
  placeholder?: string;
  createOption?: string;
  onCreate?: () => void;
  className?: string;
  disabled?: boolean;
}) {
  const blank = value === "" && !disabled;
  return (
    <select
      value={value}
      disabled={disabled}
      onChange={(e) => {
        const next = e.target.value;
        if (createOption && next === createOption) {
          onCreate?.();
          return;
        }
        onChange(next);
      }}
      className={`${inputClass} ${blank ? `${blankBorder} text-slate-500` : filledBorder} ${className}`}
    >
      {value === "" && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {createOption && <option value={createOption}>{createOption}</option>}
      {options
        .filter((opt) => opt !== "")
        .map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
    </select>
  );
}

export function RadioGroup({
  name,
  options,
  value,
  onChange,
}: {
  name: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex gap-5">
      {options.map((opt) => (
        <label
          key={opt.value}
          className="flex items-center gap-1.5 text-sm text-slate-700 dark:text-slate-200"
        >
          <input
            type="radio"
            name={name}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="h-3.5 w-3.5 accent-[var(--cobalt)]"
          />
          {opt.label}
        </label>
      ))}
    </div>
  );
}

export function Button({
  variant = "secondary",
  className = "",
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
}) {
  const variants: Record<string, string> = {
    primary:
      "bg-[var(--cobalt)] text-white hover:bg-[var(--cobalt-deep)] disabled:bg-slate-300 dark:disabled:bg-slate-700",
    secondary:
      "bg-white text-slate-700 border border-slate-300 hover:border-slate-400 hover:bg-slate-50 disabled:text-slate-400 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-600 dark:hover:bg-slate-700",
    danger: "bg-red-600 text-white hover:bg-red-700 disabled:bg-red-300",
    ghost:
      "text-slate-600 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-300 dark:hover:bg-slate-800",
  };
  return (
    <button
      {...rest}
      className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--cobalt)] disabled:cursor-not-allowed ${variants[variant]} ${className}`}
    />
  );
}
