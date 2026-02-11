interface BondTimeParamsProps {
    maturityPeriod: number;
    purchaseDate: string;
    lastUpdate?: string;
}

export default function BondTimeParams({
    maturityPeriod,
    purchaseDate,
    lastUpdate,
}: BondTimeParamsProps) {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Time Parameters
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Maturity Period</span>
                    <span className="font-semibold text-gray-900">
                        {maturityPeriod} mo
                    </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Purchase date</span>
                    <span className="font-semibold text-gray-900">
                        {new Date(purchaseDate).toLocaleDateString("en-EN", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                        })}
                    </span>
                </div>

                {lastUpdate && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                        <span className="text-gray-600">Last update</span>
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
