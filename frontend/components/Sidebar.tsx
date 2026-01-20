"use client";

import { SortControls } from "@/app/dashboard/components/SortControls";

interface SidebarProps {
    isOpen: boolean;
    onToggle: () => void;
    sortBy: "purchase_date" | "current_value";
    sortOrder: "asc" | "desc";
    onSortChange: (
        sortBy: "purchase_date" | "current_value",
        sortOrder: "asc" | "desc",
    ) => void;
    groupByDate: boolean;
    onGroupByDateChange: (value: boolean) => void;
}

export function Sidebar({
    isOpen,
    onToggle,
    sortBy,
    sortOrder,
    onSortChange,
    groupByDate,
    onGroupByDateChange,
}: SidebarProps) {
    return (
        <>
            {!isOpen && (
                <button
                    onClick={onToggle}
                    className="fixed right-8 top-32 w-14 h-14 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center z-50"
                    aria-label="Open menu"
                >
                    <svg
                        className="w-6 h-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 6h16M4 12h16M4 18h16"
                        />
                    </svg>
                </button>
            )}

            <div
                className={`bg-white border-l border-gray-200 transition-all duration-300 ease-in-out flex-shrink-0 ${
                    isOpen ? "w-80" : "w-0"
                } overflow-hidden`}
            >
                <div className="p-6 w-80">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold text-gray-900">
                            Menu
                        </h2>
                        <button
                            onClick={onToggle}
                            className="text-gray-500 hover:text-gray-700 transition-colors"
                            aria-label="Закрыть панель"
                        >
                            <svg
                                className="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>

                    <div className="mb-6">
                        <h3 className="text-sm font-medium text-gray-700 mb-3">
                            Sort by
                        </h3>
                        <SortControls
                            sortBy={sortBy}
                            sortOrder={sortOrder}
                            onSortChange={onSortChange}
                        />
                    </div>

                    <div className="mb-6 pb-6 border-b border-gray-200">
                        <label className="flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={groupByDate}
                                onChange={(e) =>
                                    onGroupByDateChange(e.target.checked)
                                }
                                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                            />
                            <span className="ml-3 text-sm font-medium text-gray-700">
                                Group by Purchase Date
                            </span>
                        </label>
                    </div>
                </div>
            </div>
        </>
    );
}
