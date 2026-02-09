import { BondHolderResponse } from "@/types/Bond";
import { ArrowUpDown, Plus } from "lucide-react";
import { useState } from "react";

interface BondsListProps {
    bonds: BondHolderResponse[];
    groupedBonds: Record<string, BondHolderResponse[]>;
    onBondClick: (bond: BondHolderResponse) => void;
    onAddClick: () => void;
}

type SortOption =
    | "series"
    | "quantity"
    | "faceValue"
    | "totalValue"
    | "purchaseDate";

export function BondsList({ bonds, onBondClick, onAddClick }: BondsListProps) {
    const [groupByDate, setGroupByDate] = useState(false);
    const [showSortMenu, setShowSortMenu] = useState(false);
    const [sortBy, setSortBy] = useState<SortOption>("series");

    const sortOptions = [
        { value: "series" as SortOption, label: "Series" },
        { value: "quantity" as SortOption, label: "Quantity" },
        { value: "faceValue" as SortOption, label: "Face Value" },
        { value: "totalValue" as SortOption, label: "Total Value" },
        { value: "purchaseDate" as SortOption, label: "Purchase Date" },
    ];

    const groupBondsByDay = (bonds: BondHolderResponse[]) => {
        return bonds.reduce(
            (acc, bond) => {
                const day = new Date(bond.purchase_date).getDate();
                const dayKey = day.toString().padStart(2, "0");

                if (!acc[dayKey]) {
                    acc[dayKey] = [];
                }
                acc[dayKey].push(bond);
                return acc;
            },
            {} as Record<string, BondHolderResponse[]>,
        );
    };

    const sortedBonds = [...bonds].sort((a, b) => {
        switch (sortBy) {
            case "series":
                return a.series.localeCompare(b.series);
            case "quantity":
                return b.quantity - a.quantity;
            case "faceValue":
                return b.nominal_value - a.nominal_value;
            case "totalValue":
                return (
                    b.nominal_value * b.quantity - a.nominal_value * a.quantity
                );
            case "purchaseDate":
                return (
                    new Date(b.purchase_date).getTime() -
                    new Date(a.purchase_date).getTime()
                );
            default:
                return 0;
        }
    });

    const groupedByDay = groupBondsByDay(sortedBonds);

    if (bonds.length === 0) {
        return (
            <div className="bg-white rounded-lg border border-gray-200">
                <div className="p-8 text-center text-gray-500">
                    You have no bonds yet
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-gray-900">Your Bondholders</h3>
                    <button
                        onClick={onAddClick}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Add Bondholder"
                    >
                        <Plus className="size-5" />
                    </button>
                </div>

                <div className="flex items-center gap-4">
                    {/* Group by Date Checkbox */}
                    <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={groupByDate}
                            onChange={(e) => setGroupByDate(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>Group by purchase date</span>
                    </label>

                    {/* Sort Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowSortMenu(!showSortMenu)}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                        >
                            <ArrowUpDown className="size-4" />
                            <span>
                                Sort by:{" "}
                                {
                                    sortOptions.find(
                                        (opt) => opt.value === sortBy,
                                    )?.label
                                }
                            </span>
                        </button>

                        {showSortMenu && (
                            <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                                {sortOptions.map((option) => (
                                    <button
                                        key={option.value}
                                        onClick={() => {
                                            setSortBy(option.value);
                                            setShowSortMenu(false);
                                        }}
                                        className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                                            sortBy === option.value
                                                ? "text-blue-600 bg-blue-50"
                                                : "text-gray-700"
                                        }`}
                                    >
                                        {option.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {!groupByDate ? (
                // Default table
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Series
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Quantity
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Face Value
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Total Value
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Purchase Date
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {sortedBonds.map((bond) => (
                                <tr
                                    key={bond.id}
                                    onClick={() => onBondClick(bond)}
                                    className="hover:bg-gray-50 cursor-pointer"
                                >
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            {bond.series}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            {bond.quantity}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm text-gray-900">
                                            $
                                            {bond.nominal_value.toLocaleString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            $
                                            {(
                                                bond.nominal_value *
                                                bond.quantity
                                            ).toLocaleString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {new Date(
                                            bond.purchase_date,
                                        ).toLocaleDateString("ru-RU")}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                // Group by purchase day
                <div>
                    {Object.entries(groupedByDay)
                        .sort(
                            ([dayA], [dayB]) => parseInt(dayA) - parseInt(dayB),
                        )
                        .map(([day, dayBonds]) => (
                            <div key={day}>
                                <div className="px-6 py-3 bg-gray-50 text-sm font-medium text-gray-700 border-b border-gray-200">
                                    Day {day} of the month ({dayBonds.length}{" "}
                                    bonds)
                                </div>
                                <div className="divide-y divide-gray-200">
                                    {dayBonds.map((bond) => (
                                        <div
                                            key={bond.id}
                                            onClick={() => onBondClick(bond)}
                                            className="px-6 py-4 hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                                        >
                                            <div>
                                                <div className="font-medium text-gray-900">
                                                    {bond.series}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    {new Date(
                                                        bond.purchase_date,
                                                    ).toLocaleDateString(
                                                        "ru-RU",
                                                    )}{" "}
                                                    · {bond.quantity} pcs · $
                                                    {bond.nominal_value.toLocaleString()}{" "}
                                                    each
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <div className="font-medium text-gray-900">
                                                    $
                                                    {(
                                                        bond.nominal_value *
                                                        bond.quantity
                                                    ).toLocaleString()}
                                                </div>
                                                <div className="text-sm text-gray-500">
                                                    Total value
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                </div>
            )}
        </div>
    );
}
