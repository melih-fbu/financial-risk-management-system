import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Ana Sayfa' },
  { to: '/simulation', label: 'Simülasyon' },
  { to: '/compare', label: 'Karşılaştırma' },
  { to: '/history', label: 'Fiyat Geçmişi' },
]

function Layout() {
  return (
    <div className="min-h-screen bg-halo text-ink">
      <header className="sticky top-0 z-20 border-b border-white/70 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">
              Finansal Risk Yönetimi
            </p>
            <h1 className="text-2xl font-bold text-slate-900">
              Çok Katmanlı Veri Tabanı Tabanlı Finansal Risk Yönetimi Sistemi
            </h1>
          </div>

          <nav className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 text-sm font-semibold transition ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-soft'
                      : 'bg-white text-slate-700 hover:bg-slate-100'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
