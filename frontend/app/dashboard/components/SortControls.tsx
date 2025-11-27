interface SortControlsProps {
  sortBy: 'purchase_date' | 'current_value';
  sortOrder: 'asc' | 'desc';
  onSortChange: (sortBy: 'purchase_date' | 'current_value', sortOrder: 'asc' | 'desc') => void;
}

export function SortControls({ sortBy, sortOrder, onSortChange }: SortControlsProps) {
  const getCurrentLabel = () => {
    if (sortBy === 'purchase_date' && sortOrder === 'desc') return 'Самые новые';
    if (sortBy === 'purchase_date' && sortOrder === 'asc') return 'Самые старые';
    if (sortBy === 'current_value' && sortOrder === 'desc') return 'Наиболее дорогие';
    if (sortBy === 'current_value' && sortOrder === 'asc') return 'Наиболее дешевые';
    return 'Сортировка';
  };

  return (
    <div className="mb-6 relative inline-block">
      <select
        value={`${sortBy}-${sortOrder}`}
        onChange={(e) => {
          const [newSortBy, newSortOrder] = e.target.value.split('-') as ['purchase_date' | 'current_value', 'asc' | 'desc'];
          onSortChange(newSortBy, newSortOrder);
        }}
        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
      >
        <option value="purchase_date-desc">Самые новые</option>
        <option value="purchase_date-asc">Самые старые</option>
        <option value="current_value-desc">Наиболее дорогие</option>
        <option value="current_value-asc">Наиболее дешевые</option>
      </select>
    </div>
  );
}
