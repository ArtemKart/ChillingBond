interface BondTimeParamsProps {
    maturityPeriod: number;
    purchaseDate: string;
    lastUpdate?: string;
    isEditing: boolean;
    onMaturityPeriodChange: (value: number) => void;
}

export default function BondTimeParams({
    maturityPeriod,
    purchaseDate,
    lastUpdate,
    isEditing,
    onMaturityPeriodChange,
}: BondTimeParamsProps) {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Time Parameters
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Срок погашения</span>
                    {isEditing ? (
                        <div className="flex items-center gap-1">
                            <input
                                type="number"
                                value={maturityPeriod}
                                onChange={(e) =>
                                    onMaturityPeriodChange(
                                        parseInt(e.target.value),
                                    )
                                }
                                className="font-semibold text-gray-900 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                            />
                            <span className="font-semibold text-gray-900">
                                мес.
                            </span>
                        </div>
                    ) : (
                        <span className="font-semibold text-gray-900">
                            {maturityPeriod} мес.
                        </span>
                    )}
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Дата покупки</span>
                    <span className="font-semibold text-gray-900">
                        {new Date(purchaseDate).toLocaleDateString("ru-RU", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                        })}
                    </span>
                </div>

                {lastUpdate && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                        <span className="text-gray-600">
                            Last update
                        </span>
                        <span className="font-semibold text-gray-900">
                            {new Date(lastUpdate).toLocaleString("ru-RU", {
                                year: "numeric",
                                month: "long",
                                day: "numeric",
                                hour: "2-digit",
                                minute: "2-digit",
                            })}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}
