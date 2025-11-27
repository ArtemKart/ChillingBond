interface BondModalHeaderProps {
    series: string;
    onClose: () => void;
}

export default function BondModalHeader({
    series,
    onClose,
}: BondModalHeaderProps) {
    return (
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">
                Облигация {series}
            </h2>
            <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
                ×
            </button>
        </div>
    );
}
