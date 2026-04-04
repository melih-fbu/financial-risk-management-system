function SectionHeader({ eyebrow, title, description }) {
  return (
    <div className="max-w-3xl space-y-3">
      <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-500">{eyebrow}</p>
      <h2 className="text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">{title}</h2>
      <p className="text-base leading-7 text-slate-600 md:text-lg">{description}</p>
    </div>
  )
}

export default SectionHeader
