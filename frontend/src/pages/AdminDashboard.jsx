import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import ItemCard from '../components/ItemCard'
import FilterBar from '../components/FilterBar'
import ItemFormModal from '../components/ItemFormModal'

export default function AdminDashboard() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | { mode: 'add' } | { mode: 'edit', item }
  const navigate = useNavigate()

  const fetchItems = () => {
    api.get('/items').then((res) => {
      setItems(res.data)
      setLoading(false)
    })
  }

  useEffect(() => { fetchItems() }, [])

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

  const handleSave = async (fd) => {
    if (modal.mode === 'add') {
      await api.post('/items', fd)
    } else {
      await api.put(`/items/${modal.item.id}`, fd)
    }
    setModal(null)
    fetchItems()
  }

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete "${item.title}"?`)) return
    await api.delete(`/items/${item.id}`)
    fetchItems()
  }

  const handleToggleSold = async (item) => {
    const fd = new FormData()
    fd.append('sold', String(!item.sold))
    await api.put(`/items/${item.id}`, fd)
    fetchItems()
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    navigate('/admin/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">JimmyStore — Admin</h1>
        <div className="flex gap-3">
          <button
            onClick={() => setModal({ mode: 'add' })}
            className="bg-indigo-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-indigo-700"
          >
            + Add Item
          </button>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-gray-600"
          >
            Logout
          </button>
        </div>
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
              <ItemCard
                key={item.id}
                item={item}
                adminMode={true}
                onEdit={(item) => setModal({ mode: 'edit', item })}
                onDelete={handleDelete}
                onToggleSold={handleToggleSold}
              />
            ))}
          </div>
        )}
      </main>

      {modal && (
        <ItemFormModal
          item={modal.mode === 'edit' ? modal.item : null}
          onSave={handleSave}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  )
}
