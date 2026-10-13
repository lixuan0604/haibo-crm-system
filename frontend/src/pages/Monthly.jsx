import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { createCategory, downloadCsv, getMonthly, saveMonthly } from "../api";
import { addMoney, money } from "../format";
import { useHealth } from "../health";

export default function Monthly() {
  const { health } = useHealth();
  const [year, setYear] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const activeYear = year || health?.importYear || 2026;

  async function load(targetYear = activeYear) {
    setError("");
    try {
      setData(await getMonthly(targetYear));
    } catch (reason) {
      setError(reason.message);
    }
  }

  useEffect(() => {
    if (health?.database === "ready") load(activeYear);
  }, [health, activeYear]);

  const cells = useMemo(() => {
    const map = new Map();
    for (const cell of data?.cells || []) map.set(`${cell.month}:${cell.category}`, cell.amount);
    return map;
  }, [data]);

  const years = useMemo(() => {
    const values = new Set(data?.years || []);
    values.add(activeYear);
    return [...values].sort((a, b) => a - b);
  }, [data, activeYear]);

  async function saveCell(month, category, amount) {
    await saveMonthly({ year: activeYear, month, category, amount });
    await load(activeYear);
  }

  async function exportYear() {
    setError("");
    try {
      await downloadCsv(`/api/reports/monthly.csv?year=${activeYear}`, `${activeYear}年每月费用.csv`);
    } catch (reason) {
      setError(reason.message);
    }
  }

  async function addCategory(event) {
    event.preventDefault();
    if (!categoryName.trim()) return;
    setError("");
    try {
      await createCategory(categoryName.trim());
      setCategoryName("");
      await load(activeYear);
    } catch (reason) {
      setError(reason.message);
    }
  }

  const categories = data?.categories || [];

  return (
    <section>
      <header className="page-head">
        <div>
          <h1>每月费用</h1>
          <p>电费、水费、宿舍这些按月记。空着是还没记，填 0 表示这个月确实没有。</p>
        </div>
        {health?.database === "ready" && (
          <div className="toolbar no-print">
            <select value={activeYear} onChange={(event) => setYear(Number(event.target.value))}>
              {years.map((item) => (
                <option key={item} value={item}>
                  {item}年
                </option>
              ))}
            </select>
            <button type="button" className="btn" onClick={() => setYear(activeYear + 1)}>
              下一年
            </button>
            <button type="button" className="btn" onClick={exportYear} disabled={!data}>
              导出
            </button>
            <button type="button" className="btn" onClick={() => window.print()} disabled={!data}>
              打印
            </button>
          </div>
        )}
      </header>
      {error && <div className="banner error">{error}</div>}
      {health && health.database !== "ready" && (
        <div className="banner">
          数据库还没准备好。先到<Link to="/">汇总</Link>看连接状态。
        </div>
      )}
      {health?.database === "ready" && data && (
        <>
          <div className="table-wrap">
            <table className="month-table">
              <thead>
                <tr>
                  <th>月份</th>
                  {categories.map((category) => (
                    <th key={category} className="num">
                      {category}
                    </th>
                  ))}
                  <th className="num">合计</th>
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: 12 }, (_, index) => index + 1).map((month) => {
                  const values = categories.map((category) => cells.get(`${month}:${category}`) ?? null);
                  const total = values.some((value) => value !== null && value !== undefined) ? addMoney(values) : null;
                  return (
                    <tr key={month}>
                      <td>{month}月</td>
                      {categories.map((category) => (
                        <td key={category} className="num">
                          <AmountCell
                            amount={cells.has(`${month}:${category}`) ? cells.get(`${month}:${category}`) : null}
                            onSave={(amount) => saveCell(month, category, amount)}
                          />
                        </td>
                      ))}
                      <td className="num total">{total === null ? "未记" : money(total)}</td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr>
                  <td>合计</td>
                  {categories.map((category) => {
                    const values = [];
                    for (let month = 1; month <= 12; month += 1) {
                      if (cells.has(`${month}:${category}`)) values.push(cells.get(`${month}:${category}`));
                    }
                    return (
                      <td key={category} className="num">
                        {values.length ? money(addMoney(values)) : "未记"}
                      </td>
                    );
                  })}
                  <td className="num">{money(data.total)}</td>
                </tr>
              </tfoot>
            </table>
          </div>
          <form className="inline-form no-print" onSubmit={addCategory}>
            <input
              value={categoryName}
              onChange={(event) => setCategoryName(event.target.value)}
              placeholder="新科目，例如停车费"
            />
            <button type="submit" className="btn">
              添加科目
            </button>
          </form>
        </>
      )}
    </section>
  );
}

function AmountCell({ amount, onSave }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const empty = amount === null || amount === undefined;

  async function commit() {
    const text = draft.trim().replace(/,/g, "").replace(/，/g, "");
    try {
      if (text === "") await onSave(null);
      else {
        const number = Number(text);
        if (!Number.isFinite(number)) {
          setError("金额不对");
          return;
        }
        await onSave(number);
      }
      setEditing(false);
      setError("");
    } catch (reason) {
      setError(reason.message);
    }
  }

  if (editing) {
    return (
      <span className="cell-edit">
        <input
          autoFocus
          inputMode="decimal"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onBlur={commit}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              event.currentTarget.blur();
            }
            if (event.key === "Escape") {
              setEditing(false);
              setError("");
            }
          }}
        />
        {error && <em>{error}</em>}
      </span>
    );
  }

  return (
    <button
      type="button"
      className={empty ? "cell-btn empty" : "cell-btn"}
      onClick={() => {
        setDraft(empty ? "" : String(amount));
        setEditing(true);
      }}
    >
      {empty ? "未记" : money(amount)}
    </button>
  );
}
