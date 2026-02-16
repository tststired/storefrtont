export default function FilterBar({
  category, setCategory,
  statusFilter, setStatusFilter,
  search, setSearch,
}) {
  const categoryTabs = [
    { value: '', label: 'All' },
    { value: 'mice', label: 'Mice' },
    { value: 'mousepads', label: 'Mousepads' },
  ]

  const statusTabs = [
    { value: '', label: 'All' },
    { value: 'false', label: 'Available' },
    { value: 'true', label: 'Sold' },
  ]

  return (
    <div className="flex flex-col gap-3 mb-6">
      {/* Search */}
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search items..."
        className="w-full max-w-sm border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />

      {/* Category tabs */}
      <div className="flex gap-2 flex-wrap">
        {categoryTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setCategory(tab.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              category === tab.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Status tabs */}
      <div className="flex gap-2 flex-wrap">
        {statusTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              statusFilter === tab.value
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}
