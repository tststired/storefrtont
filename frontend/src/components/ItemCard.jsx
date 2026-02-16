export default function ItemCard({ item, adminMode, onEdit, onDelete, onToggleSold }) {
  const imageUrl = item.image_filename
    ? `/api/uploads/${item.image_filename}`
    : null

  return (
    <div className="relative bg-white rounded-2xl shadow hover:shadow-lg transition overflow-hidden flex flex-col">
      {/* Image */}
      <div className="relative bg-gray-100 h-48 flex items-center justify-center">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={item.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-sm">No image</span>
        )}
        {item.sold && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <span className="text-white font-bold text-2xl tracking-widest rotate-[-15deg] border-4 border-white px-4 py-1 rounded">
              SOLD
            </span>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-4 flex flex-col gap-1 flex-1">
        <h2 className="font-semibold text-gray-900 text-base leading-tight">{item.title}</h2>
        <p className="text-indigo-600 font-bold text-lg">${item.price.toFixed(2)}</p>
        <span className="text-xs text-gray-400 capitalize">{item.category}</span>
      </div>

      {/* Admin actions */}
      {adminMode && (
        <div className="px-4 pb-4 flex gap-2 flex-wrap">
          <button
            onClick={() => onEdit(item)}
            className="text-xs bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full hover:bg-indigo-200"
          >
            Edit
          </button>
          <button
            onClick={() => onToggleSold(item)}
            className={`text-xs px-3 py-1 rounded-full ${
              item.sold
                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
            }`}
          >
            {item.sold ? 'Unmark Sold' : 'Mark Sold'}
          </button>
          <button
            onClick={() => onDelete(item)}
            className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded-full hover:bg-red-200"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  )
}
