export function money(value) {
  if (value === null || value === undefined || value === "") return "—";
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  return number.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function addMoney(values) {
  const cents = values.reduce((sum, value) => {
    if (value === null || value === undefined || value === "") return sum;
    const number = Number(value);
    if (Number.isNaN(number)) return sum;
    return sum + Math.round(number * 100);
  }, 0);
  return (cents / 100).toFixed(2);
}

export function unpaidText(value) {
  const number = Number(value);
  if (Number.isNaN(number)) return "—";
  if (number < 0) return `超付 ${money(Math.abs(number))}`;
  return money(number);
}
