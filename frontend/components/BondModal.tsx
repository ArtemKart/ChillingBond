"use client";

import { useState } from "react";
import type { BondHolderResponse } from "@/types/bond";
import { fetchWithAuth } from "@/lib/api";

interface BondModalProps {
    bond: BondHolderResponse;
    onClose: () => void;
    onUpdate?: () => void;
}

export default function BondModal({ bond, onClose, onUpdate }: BondModalProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isChangingQuantity, setIsChangingQuantity] = useState(false);
    const [error, setError] = useState("");
    const [quantityError, setQuantityError] = useState("");
    const [showQuantityInput, setShowQuantityInput] = useState(false);
    const [quantityToChange, setQuantityToChange] = useState(1);

    // Состояние для редактируемых полей
    const [editedBond, setEditedBond] = useState({
        series: bond.series,
        nominal_value: bond.nominal_value,
        maturity_period: bond.maturity_period,
        initial_interest_rate: bond.initial_interest_rate,
        first_interest_period: bond.first_interest_period,
        reference_rate_margin: bond.reference_rate_margin,
    });

    const handleEdit = () => {
        setIsEditing(true);
        setError("");
    };

    const handleCancel = () => {
        setIsEditing(false);
        setError("");
        setEditedBond({
            series: bond.series,
            nominal_value: bond.nominal_value,
            maturity_period: bond.maturity_period,
            initial_interest_rate: bond.initial_interest_rate,
            first_interest_period: bond.first_interest_period,
            reference_rate_margin: bond.reference_rate_margin,
        });
    };

    const handleDelete = async () => {
        try {
            const response = await fetchWithAuth(`/bonds/${bond.bond_id}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail || "Не удалось удалить облигации",
                );
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ошибка удаления");
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setError("");

        try {
            const response = await fetchWithAuth(
                `/bonds/${bond.bond_id}/specification`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(editedBond),
                },
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail || "Не удалось сохранить изменения",
                );
            }

            setIsEditing(false);

            if (onUpdate) {
                onUpdate();
            }

            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ошибка сохранения");
        } finally {
            setIsSaving(false);
        }
    };

    const handleChange = (
        field: keyof typeof editedBond,
        value: string | number,
    ) => {
        setEditedBond((prev) => ({
            ...prev,
            [field]: value,
        }));
    };

    const handleChangeQuantity = async (isPositive: boolean) => {
        if (quantityToChange <= 0) {
            setQuantityError("Количество должно быть больше 0");
            return;
        }

        if (!isPositive && quantityToChange > bond.quantity) {
            setQuantityError(
                `Невозможно уменьшить на ${quantityToChange}. У вас только ${bond.quantity} шт.`,
            );
            return;
        }

        setIsChangingQuantity(true);
        setQuantityError("");

        try {
            const response = await fetchWithAuth(`/bonds/${bond.id}/add`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    quantity: quantityToChange,
                    is_positive: isPositive,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail || "Не удалось изменить количество",
                );
            }

            setShowQuantityInput(false);
            setQuantityToChange(1);

            if (onUpdate) {
                onUpdate();
            }

            onClose();
        } catch (err) {
            setQuantityError(
                err instanceof Error
                    ? err.message
                    : "Ошибка изменения количества",
            );
        } finally {
            setIsChangingQuantity(false);
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
                        Облигация {isEditing ? editedBond.series : bond.series}
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
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-500 mb-1">
                                    Серия
                                </p>
                                {isEditing ? (
                                    <input
                                        type="text"
                                        value={editedBond.series}
                                        onChange={(e) =>
                                            handleChange(
                                                "series",
                                                e.target.value,
                                            )
                                        }
                                        className="text-xl font-bold text-gray-900 w-full bg-white border border-gray-300 rounded px-2 py-1"
                                    />
                                ) : (
                                    <p className="text-xl font-bold text-gray-900">
                                        {bond.series}
                                    </p>
                                )}
                            </div>

                            <div className="bg-blue-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-500 mb-2">
                                    Количество
                                </p>

                                {!showQuantityInput ? (
                                    <div className="flex items-center gap-2">
                                        <p className="text-xl font-bold text-blue-600">
                                            {bond.quantity} шт.
                                        </p>
                                        <button
                                            onClick={() =>
                                                setShowQuantityInput(true)
                                            }
                                            className="ml-auto text-blue-600 hover:text-blue-800 text-sm font-medium"
                                        >
                                            Изменить
                                        </button>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {quantityError && (
                                            <p className="text-xs text-red-600">
                                                {quantityError}
                                            </p>
                                        )}
                                        <div className="flex items-center gap-2">
                                            <input
                                                type="number"
                                                min="1"
                                                value={quantityToChange}
                                                onChange={(e) =>
                                                    setQuantityToChange(
                                                        parseInt(
                                                            e.target.value,
                                                        ) || 1,
                                                    )
                                                }
                                                className="w-20 px-2 py-1 border border-gray-300 rounded text-center"
                                                disabled={isChangingQuantity}
                                            />
                                            <button
                                                onClick={() =>
                                                    handleChangeQuantity(false)
                                                }
                                                disabled={isChangingQuantity}
                                                className="flex-1 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 text-sm font-medium"
                                            >
                                                −
                                            </button>
                                            <button
                                                onClick={() =>
                                                    handleChangeQuantity(true)
                                                }
                                                disabled={isChangingQuantity}
                                                className="flex-1 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 text-sm font-medium"
                                            >
                                                +
                                            </button>
                                        </div>
                                        <button
                                            onClick={() => {
                                                setShowQuantityInput(false);
                                                setQuantityError("");
                                                setQuantityToChange(1);
                                            }}
                                            className="text-xs text-gray-500 hover:text-gray-700"
                                        >
                                            Отмена
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Финансовые параметры */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Финансовые параметры
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Номинальная стоимость
                                </span>
                                {isEditing ? (
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={editedBond.nominal_value}
                                        onChange={(e) =>
                                            handleChange(
                                                "nominal_value",
                                                parseFloat(e.target.value),
                                            )
                                        }
                                        className="font-semibold text-gray-900 w-32 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                                    />
                                ) : (
                                    <span className="font-semibold text-gray-900">
                                        {bond.nominal_value.toLocaleString()} ₽
                                    </span>
                                )}
                            </div>

                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Начальная процентная ставка
                                </span>
                                {isEditing ? (
                                    <div className="flex items-center gap-1">
                                        <input
                                            type="number"
                                            step="0.01"
                                            value={
                                                editedBond.initial_interest_rate
                                            }
                                            onChange={(e) =>
                                                handleChange(
                                                    "initial_interest_rate",
                                                    parseFloat(e.target.value),
                                                )
                                            }
                                            className="font-semibold text-green-600 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                                        />
                                        <span className="font-semibold text-green-600">
                                            %
                                        </span>
                                    </div>
                                ) : (
                                    <span className="font-semibold text-green-600">
                                        {bond.initial_interest_rate}%
                                    </span>
                                )}
                            </div>

                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Маржа к ставке
                                </span>
                                {isEditing ? (
                                    <div className="flex items-center gap-1">
                                        <input
                                            type="number"
                                            step="0.01"
                                            value={
                                                editedBond.reference_rate_margin
                                            }
                                            onChange={(e) =>
                                                handleChange(
                                                    "reference_rate_margin",
                                                    parseFloat(e.target.value),
                                                )
                                            }
                                            className="font-semibold text-gray-900 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                                        />
                                        <span className="font-semibold text-gray-900">
                                            %
                                        </span>
                                    </div>
                                ) : (
                                    <span className="font-semibold text-gray-900">
                                        {bond.reference_rate_margin > 0
                                            ? "+"
                                            : ""}
                                        {bond.reference_rate_margin}%
                                    </span>
                                )}
                            </div>

                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Первый процентный период
                                </span>
                                {isEditing ? (
                                    <div className="flex items-center gap-1">
                                        <input
                                            type="number"
                                            value={
                                                editedBond.first_interest_period
                                            }
                                            onChange={(e) =>
                                                handleChange(
                                                    "first_interest_period",
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
                                        {bond.first_interest_period} мес.
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Сроки */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Временные параметры
                        </h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Срок погашения
                                </span>
                                {isEditing ? (
                                    <div className="flex items-center gap-1">
                                        <input
                                            type="number"
                                            value={editedBond.maturity_period}
                                            onChange={(e) =>
                                                handleChange(
                                                    "maturity_period",
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
                                        {bond.maturity_period} мес.
                                    </span>
                                )}
                            </div>

                            <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                <span className="text-gray-600">
                                    Дата покупки
                                </span>
                                <span className="font-semibold text-gray-900">
                                    {new Date(
                                        bond.purchase_date,
                                    ).toLocaleDateString("ru-RU", {
                                        year: "numeric",
                                        month: "long",
                                        day: "numeric",
                                    })}
                                </span>
                            </div>

                            {bond.last_update && (
                                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <span className="text-gray-600">
                                        Последнее обновление
                                    </span>
                                    <span className="font-semibold text-gray-900">
                                        {new Date(
                                            bond.last_update,
                                        ).toLocaleString("ru-RU", {
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

                    {/* Расчётные данные */}
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-3">
                            Расчётные показатели
                        </h3>
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Общая стоимость портфеля
                                </span>
                                <span className="font-bold text-gray-900 text-lg">
                                    {(
                                        (isEditing
                                            ? editedBond.nominal_value
                                            : bond.nominal_value) *
                                        bond.quantity
                                    ).toLocaleString()}{" "}
                                    ₽
                                </span>
                            </div>

                            <div className="flex justify-between">
                                <span className="text-gray-600">
                                    Годовой доход (ожидаемый)
                                </span>
                                <span className="font-bold text-green-600 text-lg">
                                    {(
                                        ((isEditing
                                            ? editedBond.nominal_value
                                            : bond.nominal_value) *
                                            bond.quantity *
                                            (isEditing
                                                ? editedBond.initial_interest_rate
                                                : bond.initial_interest_rate)) /
                                        100
                                    ).toLocaleString()}{" "}
                                    ₽
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-between items-center gap-2">
                    {isEditing ? (
                        <>
                            <div></div> {/* Пустой div для баланса */}
                            <div className="flex gap-2">
                                <button
                                    onClick={handleCancel}
                                    disabled={isSaving}
                                    className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium disabled:opacity-50"
                                >
                                    Отменить
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={isSaving}
                                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 flex items-center gap-2"
                                >
                                    {isSaving ? (
                                        <>
                                            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                            Сохранение...
                                        </>
                                    ) : (
                                        "Сохранить"
                                    )}
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <button
                                onClick={handleDelete}
                                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                            >
                                Удалить
                            </button>
                            <div className="flex gap-2">
                                <button
                                    onClick={onClose}
                                    className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                                >
                                    Закрыть
                                </button>
                                <button
                                    onClick={handleEdit}
                                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                                >
                                    Редактировать
                                </button>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
