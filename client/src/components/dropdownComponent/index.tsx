import { Listbox, Transition } from "@headlessui/react";
import { Fragment, useState } from "react";
import { DropDownComponentType } from "../../constants";

export default function Dropdown({
  value,
  options,
  onSelect,
}: DropDownComponentType) {
  let [internalValue, setInternalValue] = useState(
    value === "" || !value ? "Choose an option" : value
  );
  return (
    <>
      <Listbox
        value={internalValue}
        onChange={(value) => {
          setInternalValue(value);
          onSelect(value);
        }}
      >
        {({ open }) => (
          <>
            <div className="relative mt-1">
              <Listbox.Button className="relative w-full cursor-default rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-left shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:text-sm">
                <span className="block w-max truncate">{internalValue}</span>
                <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2"></span>
              </Listbox.Button>

              <Transition
                show={open}
                as={Fragment}
                leave="transition ease-in duration-100"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
              >
                <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                  {options?.map((option: any, id) => (
                    <Listbox.Option
                      key={id}
                      className={
                        "relative cursor-default select-none py-2 pl-3 pr-9"
                      }
                      value={option}
                    >
                      {({ selected, active }) => (
                        <>
                          <span>{option}</span>

                          {selected ? (
                            <span
                              className={
                                "absolute inset-y-0 right-0 flex items-center pr-4"
                              }
                            ></span>
                          ) : null}
                        </>
                      )}
                    </Listbox.Option>
                  ))}
                </Listbox.Options>
              </Transition>
            </div>
          </>
        )}
      </Listbox>
    </>
  );
}
