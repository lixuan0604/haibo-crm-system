import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { downloadCsv, getSummary, importExcel, initDatabase } from "../api";
import { money } from "../format";
import { useHealth } from "../health";

export default function Summary() {
  const { health, refresh } = useHealth();
  const [year, setYear] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");

  const activeYear = year || health?.importYear || 2026;

  useEffect(() => {
    if (health?.database !== "ready") {
      setData(null);
      return undefined;
    }
    let cancelled = false;
    setError("");
    getSummary(activeYear)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((reason) => {
        if (!cancelled) setError(reason.message);
      });
    return () => {
      cancelled = true;
    };
  }, [health, activeYear]);

  async function setup() {
    setBusy("init");
    setError("");
    setMessage("");
    try {
      await initDatabase();
      await refresh();
      setMessage("数据表已建好，可以导入现有表格。");
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy("");
    }
  }

  async function runImport() {
    setBusy("import");
    setError("");
    setMessage("");
    try {
      const result = await importExcel();
      setMessage(
        `已导入 ${result.fixedCount} 项固定费用、${result.paymentCount} 笔付款、${result.monthlyYear} 年 ${result.monthlyCount} 笔每月费用。`
      );
      setYear(result.monthlyYear);
      await refresh();
      setData(await getSummary(result.monthlyYear));
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy("");
    }
  }

  async function exportUnpaid() {
    setError("");
    try {
      await downloadCsv("/api/reports/unpaid.csv", "未付清单.csv");
    } catch (reason) {
      setError(reason.message);
    }
  }

  return (
    <section>
      <header className="page-head">
        <div>
          <h1>汇总</h1>
          <p>固定费用按合同年度计，每月费用按实际发生计，两笔分开，不加在一起。</p>
        </div>
        {health?.database === "ready" && data && (
          <div className="toolbar no-print">
            {!data.fixedCount && (
              <button type="button" className="btn" onClick={runImport} disabled={Boolean(busy)}>
                {busy === "import" ? "正在导入…" : "导入现有表格"}
              </button>
            )}
            {data.fixedCount > 0 && (
              <>
                <button type="button" className="btn" onClick={exportUnpaid}>
                  导出未付
                </button>
                <button type="button" className="btn" onClick={() => window.print()}>
                  打印
                </button>
              </>
            )}
          </div>
        )}
      </header>

      {error && <div className="banner error">{error}</div>}
      {message && <div className="banner ok">{message}</div>}
      <Setup health={health} busy={busy} onInit={setup} />

      {health?.database === "ready" && data && (
        <>
          <div className="cards">
            <article className="card">
              <div className="label">固定费用年度</div>
              <div className="value">{money(data.annualAmount)}</div>
              <div className="hint">{data.fixedCount} 项</div>
            </article>
            <article className="card">
              <div className="label">已付</div>
              <div className="value">{money(data.paidAmount)}</div>
            </article>
            <article className="card danger">
              <div className="label">未付</div>
              <div className="value">{money(data.unpaidAmount)}</div>
              <div className="hint">{data.unpaidCount} 项还没付清</div>
            </article>
            <article className="card">
              <div className="label">{activeYear} 年每月费用</div>
              <div className="value">{money(data.monthlyTotal)}</div>
              <div className="hint">已记 {data.recordedMonths} 个月</div>
            </article>
          </div>

          <div className="split">
            <section className="panel">
              <div className="panel-head">
                <h2>还没付清</h2>
              </div>
              {data.unpaidPreview.length === 0 ? (
                <p className="muted">目前没有未付。</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>费用</th>
                      <th>起止日期</th>
                      <th className="num">未付</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.unpaidPreview.map((item) => (
                      <tr key={item.id}>
                        <td>
                          {item.parentName ? `${item.parentName} / ` : ""}
                          {item.name}
                        </td>
                        <td>{item.periodText || "—"}</td>
                        <td className="num debt">{money(item.unpaidAmount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
            <section className="panel">
              <div className="panel-head">
                <h2>{activeYear} 年各月合计</h2>
                <Link to="/monthly">按科目看</Link>
              </div>
              <table>
                <thead>
                  <tr>
                    <th>月份</th>
                    <th className="num">合计</th>
                  </tr>
                </thead>
                <tbody>
                  {data.monthTotals.map((item) => (
                    <tr key={item.month}>
                      <td>{item.month}月</td>
                      <td className="num">{item.total === null ? "未记" : money(item.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </div>
        </>
      )}
    </section>
  );
}

function Setup({ health, busy, onInit }) {
  if (!health) return <p className="muted">正在连接后端…</p>;
  if (health.database === "ready") return null;
  if (health.database === "unconfigured") {
    return (
      <div className="banner">
        数据库连接还空着。把阿里云 MySQL 的地址、账号、库名填进 backend/config.py，重启后端后再打开这个页面。
      </div>
    );
  }
  if (health.database === "unreachable") {
    return <div className="banner error">数据库没有连上。{health.error || ""}</div>;
  }
  if (health.database === "empty") {
    return (
      <div className="banner">
        <p>已经连上数据库，数据表还没建。</p>
        <button type="button" className="btn primary" onClick={onInit} disabled={Boolean(busy)}>
          {busy === "init" ? "正在建表…" : "初始化数据表"}
        </button>
      </div>
    );
  }
  return null;
}
