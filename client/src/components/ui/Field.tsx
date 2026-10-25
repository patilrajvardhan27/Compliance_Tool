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
    <section className={`card p-6 max-sm:p-5 ${className}`}>
      <header className="mb-5">
        <h2 className="text-[21px] leading-[1.19] tracking-[-0.2px]">{title}</h2>
        {hint && <p className="mt-1 text-[13px] text-muted">{hint}</p>}
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
    <label className="grid grid-cols-[minmax(160px,220px)_1fr] items-center gap-3 max-sm:grid-cols-1 max-sm:gap-1.5">
      <span className="text-[14px] text-muted">{label}</span>
      <div>{children}</div>
    </label>
  );
}

const inputClass =
  "field w-full px-3 py-2 text-[15px] text-body disabled:bg-mist disabled:text-faint max-sm:text-base";

/** Empty required-style fields get a quiet ochre cast: enter a value, nothing is assumed. */
const filledBorder = "";
const blankBorder = "border-warning/50 bg-warning-wash";

export function TextInput({
  required,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  // The "enter a value" cast only applies to required fields left blank.
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
      className={`${inputClass} nums ${blank ? blankBorder : filledBorder} ${rest.className ?? ""}`}
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
      className={`${inputClass} ${blank ? `${blankBorder} text-muted` : filledBorder} ${className}`}
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
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <label
          key={opt.value}
          className={`chip flex cursor-pointer items-center gap-2 px-3.5 py-2 text-[14px] text-body ${
            value === opt.value ? "is-selected" : ""
          }`}
        >
          <input
            type="radio"
            name={name}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="h-3.5 w-3.5 accent-[var(--color-primary)]"
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
    primary: "btn btn-primary btn-sm",
    secondary: "btn btn-secondary btn-sm",
    danger: "btn btn-sm bg-error text-white hover:bg-error/90",
    ghost:
      "btn btn-sm rounded-field px-3 text-muted hover:bg-mist hover:text-body",
  };
  return <button {...rest} className={`${variants[variant]} ${className}`} />;
}
