import type { Accessor, Component, Setter, Signal } from 'solid-js';
import { For, Show, createSignal } from 'solid-js';
import recipesByBuilding from 'src/data/recipesByBuilding.json';
import { useOptionsContext } from 'src/providers/OptionsProvider';
import {
  makeBuildingIconPart,
  makeResourceIconPart,
} from '../functions/IconNameUtils';

export const BlueprintList: Component<{
  blueprintsSignal: Signal<string[]>;
  highlightedBlueprintSignal: Signal<string>;
  buildingsSignal: Signal<string[]>;
}> = (props) => {
  const [options] = useOptionsContext();
  const [selectedBlueprints, setSelectedBlueprints] = props.blueprintsSignal;
  const [selectedBuildings, setSelectedBuildings] = props.buildingsSignal;
  const [highlightedBlueprint, setHighlightedBlueprint] =
    props.highlightedBlueprintSignal;

  const buildings = Object.entries(recipesByBuilding);

  return (
    <>
      <div class="flex flex-wrap justify-center">
        <For each={buildings}>
          {([buildingName, recipes]) => (
            <Show when={selectedBlueprints().includes(buildingName)}>
              <div
                classList={{
                  'bg-gray-100 p-4 m-4 rounded-lg flex flex-col items-center cursor-pointer':
                    true,
                  'bg-gray-300': highlightedBlueprint() === buildingName,
                }}
                onClick={() => setHighlightedBlueprint(buildingName)}
              >
                <div class="mb-2 flex flex-col items-center">
                  <Show when={options.showBuildingIcons}>
                    <img
                      src={`./icons/buildings/84px-${makeBuildingIconPart(
                        buildingName
                      )}_icon.png`}
                      width={84}
                      height={84}
                      alt={buildingName}
                      class="rounded-md shadow-lg"
                    />
                  </Show>
                  <Show when={options.showBuildingNames}>
                    <h2 class="text-xl font-bold text-gray-500">
                      {buildingName}
                    </h2>
                  </Show>
                </div>
                <ul class="list-none">
                  <For each={recipes}>
                    {(recipe) => {
                      const [productName, amount] = Object.entries(
                        recipe.Product
                      )[0] as [string, number];
                      const ingredientSlots = [];
                      for (let i = 1; i <= 4; i++) {
                        const slot = recipe[`Ingredient_${i}`];
                        if (slot) ingredientSlots.push(slot);
                      }
                      return (
                        <li class="mb-1">
                          <div class="flex space-x-1 items-center text-sm">
                            <Show when={options.showRecipeNames}>
                              <span class="font-medium">{productName}</span>
                            </Show>
                            <Show when={options.showRecipeTime}>
                              <span class="tabular-nums text-gray-500">{String(Math.floor(recipe.Time / 60)).padStart(2, '0')}:{String(recipe.Time % 60).padStart(2, '0')}</span>
                            </Show>
                            <Show when={options.showRecipeGrade}>
                              <span class="text-yellow-600">{'★'.repeat(recipe.Grade)}</span>
                            </Show>
                          </div>
                          <Show when={options.showRecipeIcons}>
                            <div class="flex space-x-1 items-center text-xs mt-0.5">
                              <For each={ingredientSlots}>
                                {(slot, slotIdx) => (
                                  <>
                                    <span class="flex items-center space-x-0.5">
                                      <For each={Object.entries(slot)}>
                                        {([name, amt]) => (
                                          <span class="flex items-center space-x-0.5">
                                            <img
                                              src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(name)}.png`}
                                              alt={name}
                                              height={20}
                                              width={20}
                                              class="rounded-sm"
                                            />
                                            <span class="tabular-nums">{amt}</span>
                                          </span>
                                        )}
                                      </For>
                                    </span>
                                    {slotIdx() < ingredientSlots.length - 1 && <span class="mx-1">+</span>}
                                  </>
                                )}
                              </For>
                              <span class="mx-1">=</span>
                              <img
                                src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(productName)}.png`}
                                alt={productName}
                                height={20}
                                width={20}
                                class="rounded-sm shadow-lg"
                              />
                              <Show when={options.showRecipeNumber}>
                                <span class="tabular-nums font-bold">{amount}</span>
                              </Show>
                            </div>
                          </Show>
                        </li>
                      );
                    }}
                  </For>
                </ul>
              </div>
            </Show>
          )}
        </For>
      </div>
      <Show when={selectedBlueprints().length > 0}>
        <div class="flex flex-row justify-center mb-6">
          <button
            onClick={() => {
              setSelectedBuildings([
                ...selectedBuildings(),
                highlightedBlueprint(),
              ]);
              setSelectedBlueprints([]);
              setHighlightedBlueprint('');
            }}
          >
            ➕ Pick
          </button>
        </div>
      </Show>
    </>
  );
};
