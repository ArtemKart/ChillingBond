interface BondBasicInfoProps {
    series: string;
    quantity: number;
    isEditing: boolean;
    onQuantityChange: (value: number) => void;
}

export default function BondBasicInfo({
    series,
    quantity,
    isEditing,
    onQuantityChange,
}: BondBasicInfoProps) {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Basic Information
            </h3>
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Series</p>
                    <p className="text-xl font-bold text-gray-900">{series}</p>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-500 mb-1">Quantity</p>
                    {isEditing ? (
                        <input
                            type="number"
                            min="1"
                            value={quantity}
                            onChange={(e) =>
                                onQuantityChange(parseInt(e.target.value) || 1)
                            }
                            className="text-xl font-bold text-blue-600 w-full bg-white border border-gray-300 rounded px-2 py-1"
                        />
                    ) : (
                        <p className="text-xl font-bold text-blue-600">
                            {quantity} pcs
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
