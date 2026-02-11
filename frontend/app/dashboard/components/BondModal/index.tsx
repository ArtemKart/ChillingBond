"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import BondModalHeader from "./BondModalHeader";
import BondBasicInfo from "./BondBasicInfo";
import BondFinancialParams from "./BondFinancialParams";
import BondTimeParams from "./BondTimeParams";
import BondCalculations from "./BondCalculations";
import BondModalFooter from "./BondModalFooter";
import { BondHolderResponse } from "@/types/Bond";

interface BondModalProps {
    bond: BondHolderResponse;
    onClose: () => void;
    onUpdate: () => void;
}

export default function BondModal({ bond, onClose, onUpdate }: BondModalProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState("");

    const [editedBond, setEditedBond] = useState({
        series: bond.series,
        nominal_value: bond.nominal_value,
        maturity_period: bond.maturity_period,
        initial_interest_rate: bond.initial_interest_rate,
        first_interest_period: bond.first_interest_period,
        reference_rate_margin: bond.reference_rate_margin,
        quantity: bond.quantity,
    });

    const handleEdit = () => {
        setIsEditing(true);
        setError("");
        setEditedBond({
            series: bond.series,
            nominal_value: bond.nominal_value,
            maturity_period: bond.maturity_period,
            initial_interest_rate: bond.initial_interest_rate,
            first_interest_period: bond.first_interest_period,
            reference_rate_margin: bond.reference_rate_margin,
            quantity: bond.quantity,
        });
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
            quantity: bond.quantity,
        });
    };

    const handleDelete = async () => {
        if (!confirm("Are you sure you want to delete this bond?")) return;

        try {
            await apiFetch(`/bonds/${bond.id}`, {
                method: "DELETE",
            });
            onUpdate();
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Delete error");
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setError("");

        try {
            if (editedBond.quantity !== bond.quantity) {
                await apiFetch(`/bonds/${bond.id}/quantity`, {
                    method: "PATCH",
                    body: JSON.stringify({
                        new_quantity: editedBond.quantity,
                    }),
                });
            }

            onUpdate();
            setIsEditing(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Save Error");
        } finally {
            setIsSaving(false);
        }
    };

    const handleChange = (field: string, value: string | number) => {
        setEditedBond((prev: typeof editedBond) => ({
            ...prev,
            [field]: value,
        }));
    };

    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4 backdrop-blur-md bg-black/30"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[85vh] overflow-y-auto"
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
            >
                <BondModalHeader
                    series={isEditing ? editedBond.series : bond.series}
                    onClose={onClose}
                />

                <div className="p-6 space-y-6">
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <BondBasicInfo
                        series={editedBond.series}
                        quantity={editedBond.quantity}
                        isEditing={isEditing}
                        onQuantityChange={(value) =>
                            handleChange("quantity", value)
                        }
                    />

                    <BondFinancialParams
                        nominalValue={editedBond.nominal_value}
                        initialInterestRate={editedBond.initial_interest_rate}
                        referenceRateMargin={editedBond.reference_rate_margin}
                        firstInterestPeriod={editedBond.first_interest_period}
                    />

                    <BondTimeParams
                        maturityPeriod={editedBond.maturity_period}
                        purchaseDate={bond.purchase_date}
                        lastUpdate={bond.last_update || undefined}
                    />

                    <BondCalculations
                        bondHolderId={bond.id}
                        nominalValue={bond.nominal_value}
                        quantity={bond.quantity}
                        initialInterestRate={bond.initial_interest_rate}
                    />
                </div>

                <BondModalFooter
                    isEditing={isEditing}
                    isSaving={isSaving}
                    onEdit={handleEdit}
                    onCancel={handleCancel}
                    onSave={handleSave}
                    onDelete={handleDelete}
                    onClose={onClose}
                />
            </div>
        </div>
    );
}
