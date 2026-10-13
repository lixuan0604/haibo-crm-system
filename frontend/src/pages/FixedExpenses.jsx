import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { createFixedExpense, deleteFixedExpense, getFixedExpenses, updateFixedExpense } from "../api";
import ConfirmDialog from "../components/ConfirmDialog";
import Modal from "../components/Modal";
import { money, unpaidText } from "../format";
import { useHealth } from "../health";

const EMPTY_FORM = {
  id: null,
  name: "",
  note: "",
  periodText: "",
  annualAmount: "",
  parentId: "",
  payments: [],
};

export default function FixedExpenses() {
  const { health } = useHealth();
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState(null);
  const [saving, setSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  async function load() {
    setError("");
    try {
      const data = await getFixedExpenses();
      setItems(data.items || []);
    } catch (reason) {
      setError(reason.message);
    }
  }

  useEffect(() => {
    if (health?.database === "ready") load();
  }, [health]);

  const rows = useMemo(() => visibleRows(items, query), [items, query]);
  const editingRoot = form?.id ? items.find((item) => item.id === form.id) : null;

  function openCreate(parentId = "") {
    setForm({ ...EMPTY_FORM, parentId: parentId ? String(parentId) : "", payments: [] });
  }

  function openEdit(item) {
    setForm({
      id: item.id,
      name: item.name,
      note: item.note || "",
      periodText: item.periodText || "",
      annualAmount: String(item.annualAmount),
      parentId: item.parentId ? String(item.parentId) : "",
      payments: (item.payments || []).map((payment) => ({
        amount: String(payment.amount),
        paidOn: payment.paidOn || "",
        remark: payment.remark || "",
      })),
    });
  }

  async function save(event) {
    event.preventDefault();
    if (!form.name.trim()) {
      setError("请填写费用名称");
      return;
    }
    setSaving(true);
    setError("");
    const body = {
      name: form.name.trim(),
      note: form.note,
      periodText: form.periodText,
      annualAmount: form.annualAmount,
      parentId: form.parentId || null,
      payments: form.payments
        .filter((payment) => String(payment.amount).trim() !== "")
        .map((payment) => ({
          amount: payment.amount,
          paidOn: payment.paidOn || null,
          remark: payment.remark,
        })),
    };
    try {
      if (form.id) await updateFixedExpense(form.id, body);
      else await createFixedExpense(body);
      setForm(null);
      await load();
    } catch (reason) {
      setError(reason.message);
    } finally {
      setSaving(false);
    }
  }

  function askRemove(item) {
    setPendingDelete(item);
  }

  async function remove() {
    const item = pendingDelete;
    if (!item) return;
    setDeleting(true);
    setError("");
    try {
      await deleteFixedExpense(item.id);
      setPendingDelete(null);
      await load();
    } catch (reason) {
      setError(reason.message);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <section>
      <header className="page-head">
        <div>
          <h1>固定费用</h1>
          <p>合同里说好的支出。年度金额减去已付，就是还欠多少。</p>
        </div>
        {health?.database === "ready" && (
          <div className="toolbar">
            <input
              className="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="搜索费用"
            />
            <button type="button" className="btn primary" onClick={() => openCreate()}>
              新增费用
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
      {health?.database === "ready" && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>费用</th>
                <th>起止日期</th>
                <th className="num">年度金额</th>
                <th className="num">已付</th>
                <th className="num">未付</th>
                <th className="num">付款</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td colSpan="7" className="muted">
                    还没有固定费用。可以在汇总页导入现有表格，也可以直接新增。
                  </td>
                </tr>
              )}
              {rows.map(({ item, child }) => (
                <tr key={item.id} className={child ? "child" : undefined}>
                  <td>
                    <strong>{item.name}</strong>
                    {item.note && <span className="name-note">{item.note.replace(/\n/g, " ")}</span>}
                  </td>
                  <td>{item.periodText || "—"}</td>
                  <td className="num">{money(item.annualAmount)}</td>
                  <td className="num">{money(item.paidAmount)}</td>
                  <td className={`num ${Number(item.unpaidAmount) > 0 ? "debt" : "settled"}`}>
                    {unpaidText(item.unpaidAmount)}
                  </td>
                  <td className="num">{item.payments?.length || 0}</td>
                  <td>
                    <div className="actions">
                      <button type="button" onClick={() => openEdit(item)}>
                        编辑
                      </button>
                      {!child && (
                        <button type="button" onClick={() => openCreate(item.id)}>
                          子项
                        </button>
                      )}
                      <button type="button" className="danger" onClick={() => askRemove(item)}>
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {form && (
        <Modal title={form.id ? "编辑费用" : "新增费用"} onClose={() => setForm(null)}>
          <form onSubmit={save}>
            <div className="fields">
              <label className="field wide">
                <span>名称</span>
                <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
              </label>
              <label className="field">
                <span>起止日期</span>
                <input
                  value={form.periodText}
                  onChange={(event) => setForm({ ...form, periodText: event.target.value })}
                  placeholder="先按原来的文字记，例如 2026.4.1-2027.3.31"
                />
              </label>
              <label className="field">
                <span>年度金额</span>
                <input
                  inputMode="decimal"
                  value={form.annualAmount}
                  onChange={(event) => setForm({ ...form, annualAmount: event.target.value })}
                />
              </label>
              <label className="field wide">
                <span>上级费用</span>
                <select
                  value={form.parentId}
                  disabled={Boolean(editingRoot?.children?.length)}
                  onChange={(event) => setForm({ ...form, parentId: event.target.value })}
                >
                  <option value="">无</option>
                  {items
                    .filter((item) => item.id !== form.id)
                    .map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                </select>
              </label>
              <label className="field wide">
                <span>注解说明</span>
                <textarea value={form.note} onChange={(event) => setForm({ ...form, note: event.target.value })} />
              </label>
            </div>

            <div className="pay-head">
              <h3>付款记录</h3>
              <button
                type="button"
                className="btn"
                onClick={() =>
                  setForm({
                    ...form,
                    payments: [...form.payments, { amount: "", paidOn: "", remark: "" }],
                  })
                }
              >
                添加一笔
              </button>
            </div>
            {form.payments.length === 0 && <p className="muted">还没有付款。已付金额在这里记，用正数。</p>}
            {form.payments.map((payment, index) => (
              <div className="pay-row" key={index}>
                <input
                  inputMode="decimal"
                  placeholder="金额"
                  value={payment.amount}
                  onChange={(event) => updatePayment(setForm, form, index, { amount: event.target.value })}
                />
                <input
                  type="date"
                  value={payment.paidOn}
                  onChange={(event) => updatePayment(setForm, form, index, { paidOn: event.target.value })}
                />
                <input
                  placeholder="备注，付给谁也可以写在这里"
                  value={payment.remark}
                  onChange={(event) => updatePayment(setForm, form, index, { remark: event.target.value })}
                />
                <button
                  type="button"
                  className="btn ghost"
                  onClick={() =>
                    setForm({ ...form, payments: form.payments.filter((_, itemIndex) => itemIndex !== index) })
                  }
                >
                  移除
                </button>
              </div>
            ))}
            <div className="modal-actions">
              <button type="submit" className="btn primary" disabled={saving}>
                {saving ? "正在保存…" : "保存"}
              </button>
            </div>
          </form>
        </Modal>
      )}
      {pendingDelete && (
        <ConfirmDialog
          title="删除费用"
          danger
          confirmText="删除"
          busy={deleting}
          message={
            pendingDelete.children?.length
              ? `删除「${pendingDelete.name}」？它下面的子项会留下来，变成单独的费用。`
              : `删除「${pendingDelete.name}」？付款记录会一起删除。`
          }
          onConfirm={remove}
          onCancel={() => {
            if (!deleting) setPendingDelete(null);
          }}
        />
      )}
    </section>
  );
}

function updatePayment(setForm, form, index, patch) {
  setForm({
    ...form,
    payments: form.payments.map((payment, itemIndex) => (itemIndex === index ? { ...payment, ...patch } : payment)),
  });
}

function visibleRows(items, query) {
  const needle = query.trim().toLowerCase();
  const hit = (entry) => !needle || `${entry.name} ${entry.note || ""}`.toLowerCase().includes(needle);
  const rows = [];
  for (const item of items) {
    const children = item.children || [];
    if (!needle || hit(item)) {
      rows.push({ item, child: false });
      children.forEach((child) => rows.push({ item: child, child: true }));
    } else {
      const matched = children.filter(hit);
      if (matched.length) {
        rows.push({ item, child: false });
        matched.forEach((child) => rows.push({ item: child, child: true }));
      }
    }
  }
  return rows;
}
