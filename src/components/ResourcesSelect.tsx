import { Component, For, Signal, createSignal, Show } from 'solid-js';
import resources from 'src/data/ResourcesList_Grouped.json';
import { BiomeSelect } from './BiomeSelect';
import { makeResourceIconPart } from '../functions/IconNameUtils';

export const ResourcesSelect: Component<{
  signal: Signal<string[]>;
  biomeSignal: Signal<string>;
}> = (props) => {
  const goods = resources.Goods;
  const [selectedValues, setSelectedValues] = props.signal;
  const [showPicker, setShowPicker] = createSignal(false);

  const toggle = (name: string) => {
    if (selectedValues().includes(name)) {
      setSelectedValues(selectedValues().filter((v) => v !== name));
    } else {
      setSelectedValues([...selectedValues(), name]);
    }
  };

  const unselected = () => goods.filter((g) => !selectedValues().includes(g.Name));

  return (
    <div class="sm:flex sm:items-center mb-6">
      <div class="sm:w-1/6">
        <label class="block text-gray-500 font-bold sm:text-right mb-1 sm:mb-0 pr-4">
          Resources
        </label>
      </div>
      <div class="sm:w-5/6">
        <div class="flex flex-row items-center space-x-1 mb-1">
          <BiomeSelect signal={props.biomeSignal} />
          <button
            class="border rounded-sm px-2 h-8 text-sm hover:bg-gray-100"
            onClick={() => setShowPicker(!showPicker())}
          >
            + Add
          </button>
          <button
            class="border rounded-sm px-2 h-8 text-sm hover:bg-gray-100"
            onClick={() => setSelectedValues([])}
          >
            Clear
          </button>
        </div>
        <div class="flex flex-row flex-wrap gap-1">
          <For each={selectedValues()}>
            {(name) => (
              <span
                class="flex items-center space-x-1 bg-gray-100 rounded px-1 py-0.5 cursor-pointer text-sm hover:bg-red-100"
                onClick={() => toggle(name)}
                title="Click to remove"
              >
                <img
                  src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(name)}.png`}
                  alt={name}
                  height={24}
                  width={24}
                  class="rounded-sm"
                />
                <span>{name}</span>
              </span>
            )}
          </For>
        </div>
        <Show when={showPicker()}>
          <div class="flex flex-row flex-wrap gap-1 mt-1 p-2 bg-gray-50 rounded border">
            <For each={unselected()}>
              {(good) => (
                <span
                  class="flex items-center space-x-1 rounded px-1 py-0.5 cursor-pointer text-sm opacity-50 hover:opacity-100 transition-opacity"
                  onClick={() => toggle(good.Name)}
                  title={good.Name}
                >
                  <img
                    src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(good.Name)}.png`}
                    alt={good.Name}
                    height={24}
                    width={24}
                    class="rounded-sm"
                  />
                  <span>{good.Name}</span>
                </span>
              )}
            </For>
          </div>
        </Show>
      </div>
    </div>
  );
};
