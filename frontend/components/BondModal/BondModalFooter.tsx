interface BondModalFooterProps {
    isEditing: boolean;
    isSaving: boolean;
    onEdit: () => void;
    onCancel: () => void;
    onSave: () => void;
    onDelete: () => void;
    onClose: () => void;
}

export default function BondModalFooter({
    isEditing,
    isSaving,
    onEdit,
    onCancel,
    onSave,
    onDelete,
    onClose,
}: BondModalFooterProps) {
    if (isEditing) {
        return (
            <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-between items-center gap-2">
                <div></div> {/* Пустой div для баланса */}
                <div className="flex gap-2">
                    <button
                        onClick={onCancel}
                        disabled={isSaving}
                        className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium disabled:opacity-50"
                    >
                        Отменить
                    </button>
                    <button
                        onClick={onSave}
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
            </div>
        );
    }

    return (
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-between items-center gap-2">
            <button
                onClick={onDelete}
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
                    onClick={onEdit}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                    Редактировать
                </button>
            </div>
        </div>
    );
}
