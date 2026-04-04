function InfoPanel({ items }) {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      {items.map((item) => (
        <article key={item.label} className="rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-soft">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">{item.label}</p>
          <p className="mt-3 text-2xl font-bold text-slate-950">{item.value}</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
        </article>
      ))}
    </section>
  )
}

export default InfoPanel
