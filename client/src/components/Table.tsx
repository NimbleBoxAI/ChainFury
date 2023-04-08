export function Table({
  headings,
  spacing,
  values,
}: {
  headings: string[];
  spacing?: number[];
  values: string[][];
}) {
  return (
    <>
      <div className="overflow-x-auto relative rounded-[4px] prose-nbx mt-[32px]">
        <table draggable className="w-full text-sm text-left ">
          <tr className="flex bg-light-neutral-grey-100 semiBold250 text-light-neutral-grey-700 rounded-md">
            {headings?.map((val, index) => (
              <>
                <th
                  key={index}
                  style={{
                    flex: spacing?.[index] || 1,
                  }}
                  scope="col"
                  className="p-[12px] min-w-[170px]"
                >
                  {val}
                </th>
              </>
            ))}
          </tr>
          {values?.map((row, index) => (
            <tr
              className={`flex regular400 ${
                index % 2 ? "bg-light-neutral-grey-100" : ""
              }`}
              key={index}
            >
              {headings?.map((val, key) => {
                return (
                  <td
                    style={{
                      flex: spacing?.[key] || 1,
                    }}
                    scope="row"
                    key={key}
                    className="p-[12px] min-w-[170px]"
                  >
                    {row[key]}
                  </td>
                );
              })}
            </tr>
          ))}
        </table>
      </div>
    </>
  );
}
