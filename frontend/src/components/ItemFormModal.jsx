import { useState, useEffect } from 'react'

const CATEGORIES = [
  { value: 'mice', label: 'Mice' },
  { value: 'mousepads', label: 'Mousepads' },
]

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ItemFormModal({ item, onSave, onClose }) {
  const [title, setTitle] = useState(item?.title || '')
  const [price, setPrice] = useState(item?.price || '')
  const [category, setCategory] = useState(item?.category || 'mice')
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (item?.image_filename) {
      setPreview(`/api/uploads/${item.image_filename}`)
    }
  }, [item])

  const handleImage = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('title', title)
      fd.append('price', price)
      fd.append('category', category)
      if (image) fd.append('image', image)
      await onSave(fd)
    } catch {
      // Parent (AdminDashboard) handles error display
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-bold mb-4">{item ? 'Edit Item' : 'Add Item'}</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Image upload */}
          <div>
            <label className="block text-sm text-gray-600 mb-1">Image</label>
            {preview && (
              <img src={preview} alt="preview" className="w-full h-40 object-cover rounded-lg mb-2" />
            )}
            <input type="file" accept="image/*" onChange={handleImage} className="text-sm" />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Price ($)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-600 py-2 rounded-lg text-sm hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
