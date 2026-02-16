import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import ItemCard from '../components/ItemCard'
import FilterBar from '../components/FilterBar'

export default function StoreFront() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get('/items').then((res) => {
      setItems(res.data)
      setLoading(false)
    })
  }, [])

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const matchCategory = !category || item.category === category
      const matchStatus =
        statusFilter === '' ||
        (statusFilter === 'true' && item.sold) ||
        (statusFilter === 'false' && !item.sold)
      const matchSearch =
        !search || item.title.toLowerCase().includes(search.toLowerCase())
      return matchCategory && matchStatus && matchSearch
    })
  }, [items, category, statusFilter, search])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">JimmyStore</h1>
        <Link to="/admin/login" className="text-xs text-gray-400 hover:text-gray-600">
          Admin
        </Link>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <FilterBar
          category={category} setCategory={setCategory}
          statusFilter={statusFilter} setStatusFilter={setStatusFilter}
          search={search} setSearch={setSearch}
        />

        {loading ? (
          <p className="text-gray-400 text-center mt-16">Loading...</p>
        ) : filtered.length === 0 ? (
          <p className="text-gray-400 text-center mt-16">No items found.</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {filtered.map((item) => (
              <ItemCard key={item.id} item={item} adminMode={false} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
