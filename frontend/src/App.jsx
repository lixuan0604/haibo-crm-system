import { useCallback, useEffect, useState } from "react";
import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { getHealth } from "./api";
import { HealthContext } from "./health";
import FixedExpenses from "./pages/FixedExpenses";
import Monthly from "./pages/Monthly";
import Summary from "./pages/Summary";

const STATUS = {
  unconfigured: "数据库未配置",
  unreachable: "数据库未连上",
  empty: "数据表未建",
  ready: "数据库已连接",
};

export default function App() {
  const [health, setHealth] = useState(null);

  const refresh = useCallback(async () => {
    try {
      setHealth(await getHealth());
    } catch (error) {
      setHealth({
        ok: false,
        database: "unreachable",
        error: error.message,
        importYear: 2026,
      });
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <HealthContext.Provider value={{ health, refresh }}>
      <div className="shell">
        <aside className="sidebar">
          <div className="brand">
            <span className="mark">海</span>
            <div>
              <strong>海博费用</strong>
              <em>办公室统计</em>
            </div>
          </div>
          <nav className="nav">
            <NavLink to="/" end>
              汇总
            </NavLink>
            <NavLink to="/fixed">固定费用</NavLink>
            <NavLink to="/monthly">每月费用</NavLink>
          </nav>
          <div className="side-status">{health ? STATUS[health.database] || "正在检查" : "正在检查"}</div>
        </aside>
        <main className="main">
          <Routes>
            <Route path="/" element={<Summary />} />
            <Route path="/fixed" element={<FixedExpenses />} />
            <Route path="/monthly" element={<Monthly />} />
            <Route path="/reports" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </HealthContext.Provider>
  );
}
