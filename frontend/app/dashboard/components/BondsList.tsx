import { BondHolderResponse } from "@/types/bond";

interface BondsListProps {
    bonds: BondHolderResponse[];
    groupedBonds: Record<string, BondHolderResponse[]>;
    onBondClick: (bond: BondHolderResponse) => void;
}

export function BondsList({
    bonds,
    groupedBonds,
    onBondClick,
}: BondsListProps) {
    if (bonds.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow">
                <div className="p-8 text-center text-gray-500">
                    У вас пока нет облигаций
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow">
            {Object.entries(groupedBonds).map(([date, dateBonds]) => (
                <div key={date}>
                    <div className="px-6 py-3 bg-gray-100 text-sm font-medium text-gray-700 border-b border-gray-200">
                        Куплено {date}
                    </div>
                    <ul className="divide-y divide-gray-200">
                        {dateBonds.map((bond) => (
                            <li
                                key={bond.id}
                                className="p-6 hover:bg-gray-50 transition cursor-pointer"
                                onClick={() => onBondClick(bond)}
                            >
                                <div className="flex justify-between items-center">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="text-lg font-semibold text-gray-900">
                                                Серия {bond.series}
                                            </h3>
                                            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full font-semibold">
                                                {bond.quantity} шт.
                                            </span>
                                        </div>

                                        <div className="flex gap-6 text-sm text-gray-600">
                                            <div>
                                                <span className="font-medium">
                                                    Номинал:
                                                </span>{" "}
                                                {bond.nominal_value.toLocaleString()}{" "}
                                                ₽
                                            </div>
                                            <div>
                                                <span className="font-medium">
                                                    Ставка:
                                                </span>{" "}
                                                {bond.initial_interest_rate}%
                                            </div>
                                            <div>
                                                <span className="font-medium">
                                                    Куплено:
                                                </span>{" "}
                                                {new Date(
                                                    bond.purchase_date,
                                                ).toLocaleDateString("ru-RU")}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="ml-4">
                                        <span className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                            Подробнее →
                                        </span>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
}
