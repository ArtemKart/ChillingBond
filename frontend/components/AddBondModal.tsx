"use client";

import { useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface AddBondModalProps {
    onClose: () => void;
    onUpdate?: () => void;
}

export default function AddBondModal({ onClose, onUpdate }: AddBondModalProps) {
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState("");

    const [formData, setFormData] = useState({
        series: "",
        nominal_value: 1000,
        maturity_period: 1092,
        initial_interest_rate: 16.0,
        first_interest_period: 182,
        reference_rate_margin: 0.0,
        quantity: 1,
        purchase_date: new Date().toISOString().split("T")[0],
    });

    const handleChange = (
        field: keyof typeof formData,
        value: string | number,
    ) => {
        setFormData((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const handleSubmit = async () => {
        if (!formData.series.trim()) {
            setError("Укажите серию облигации");
            return;
        }

        if (formData.quantity <= 0) {
            setError("Количество должно быть больше 0");
            return;
        }

        if (formData.nominal_value <= 0) {
            setError("Номинальная стоимость должна быть больше 0");
            return;
        }

        setIsSaving(true);
        setError("");

        try {
            const response = await fetchWithAuth("/bonds", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail || "Не удалось добавить облигацию",
                );
            }

            if (onUpdate) {
                onUpdate();
            }

            onClose();
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Ошибка добавления облигации",
            );
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4 backdrop-blur-md"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[85vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                    <h2 className="text-2xl font-bold text-gray-900">
                        Добавить облигацию
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                    >
                        ×
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Ошибка */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    {/* Основная информация */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Основная информация
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Серия облигации{" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={formData.series}
                                    onChange={(e) =>
                                        handleChange("series", e.target.value)
                                    }
                                    placeholder="Например, А-001"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Количество{" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    value={formData.quantity}
                                    onChange={(e) =>
                                        handleChange(
                                            "quantity",
                                            parseInt(e.target.value) || 1,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Дата покупки{" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="date"
                                    value={formData.purchase_date}
                                    onChange={(e) =>
                                        handleChange(
                                            "purchase_date",
                                            e.target.value,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Финансовые параметры */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Финансовые параметры
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Номинальная стоимость (₽){" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    value={formData.nominal_value}
                                    onChange={(e) =>
                                        handleChange(
                                            "nominal_value",
                                            parseFloat(e.target.value) || 0,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Начальная процентная ставка (%){" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    value={formData.initial_interest_rate}
                                    onChange={(e) =>
                                        handleChange(
                                            "initial_interest_rate",
                                            parseFloat(e.target.value) || 0,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Маржа к ставке (%){" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.reference_rate_margin}
                                    onChange={(e) =>
                                        handleChange(
                                            "reference_rate_margin",
                                            parseFloat(e.target.value) || 0,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Первый процентный период (мес){" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    value={formData.first_interest_period}
                                    onChange={(e) =>
                                        handleChange(
                                            "first_interest_period",
                                            parseInt(e.target.value) || 1,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Временные параметры */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Временные параметры
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Срок погашения (мес){" "}
                                    <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    value={formData.maturity_period}
                                    onChange={(e) =>
                                        handleChange(
                                            "maturity_period",
                                            parseInt(e.target.value) || 1,
                                        )
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        disabled={isSaving}
                        className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium disabled:opacity-50"
                    >
                        Отменить
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isSaving}
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 flex items-center gap-2"
                    >
                        {isSaving ? (
                            <>
                                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                Добавление...
                            </>
                        ) : (
                            "Добавить облигацию"
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
