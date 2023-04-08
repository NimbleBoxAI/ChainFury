import { useEffect, useState } from "react";
import { FileComponentType } from "../../constants";

export default function InputFileComponent({
  value,
  onChange,
  disabled,
  suffixes,
  fileTypes,
  onFileChange,
}: FileComponentType) {
  const [myValue, setMyValue] = useState(value);
  useEffect(() => {
    if (disabled) {
      setMyValue("");
      onChange("");
      onFileChange("");
    }
  }, [disabled, onChange]);

  function attachFile(fileReadEvent: ProgressEvent<FileReader>) {
    fileReadEvent.preventDefault();
    const file = fileReadEvent?.target?.result;
    onFileChange(file as string);
  }

  function checkFileType(fileName: string): boolean {
    for (let index = 0; index < suffixes.length; index++) {
      if (fileName.endsWith(suffixes[index])) {
        return true;
      }
    }
    return false;
  }

  const handleButtonClick = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = suffixes.join(",");
    input.style.display = "none";
    input.multiple = false;
    input.onchange = (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      const fileData = new FileReader();
      fileData.onload = attachFile;
      if (file && checkFileType(file.name)) {
        fileData.readAsDataURL(file);
        setMyValue(file.name);
        onChange(file.name);
      } else {
        alert("Please select a valid file. Only files this files are allowed:");
      }
    };
    input.click();
  };

  return (
    <div
      className={
        disabled ? "pointer-events-none cursor-not-allowed w-full" : "w-full"
      }
    >
      <div className="w-full flex items-center gap-3">
        <span
          onClick={handleButtonClick}
          className={
            " truncate block w-full text-gray-500 px-3 py-2 rounded-md border border-gray-300 dark:border-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" +
            (disabled ? " bg-gray-200" : "")
          }
        >
          {myValue !== "" ? myValue : "Select file"}
        </span>
      </div>
    </div>
  );
}
