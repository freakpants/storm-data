import type { Accessor, Component } from 'solid-js';
import { For, Show, createSignal } from 'solid-js';
import recipesByBuilding from 'src/data/recipesByBuilding.json';
import { useOptionsContext } from 'src/providers/OptionsProvider';
import {
  makeBuildingIconPart,
  makeResourceIconPart,
} from '../functions/IconNameUtils';

const IngredientSlot: Component<{
  slot: Record<string, number>;
  availableGoods: Accessor<string[]>;
}> = (props) => {
  const entries = Object.entries(props.slot);
  const firstAvailable = () => entries.findIndex(([n]) => props.availableGoods().includes(n));
  const [idx, setIdx] = createSignal(firstAvailable() >= 0 ? firstAvailable() : 0);
  const selected = () => entries[idx() % entries.length];
  const isAvailable = (name: string) => props.availableGoods().includes(name);
  return (
    <span
      class="flex items-center space-x-0.5 cursor-pointer hover:bg-gray-200 rounded px-0.5 py-0.5 select-none"
      classList={{ 'opacity-40': !isAvailable(selected()[0]) }}
      onClick={(e) => { e.stopPropagation(); setIdx((i) => (i + 1) % entries.length); }}
      title="Click to switch ingredient"
    >
      <img
        src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(selected()[0])}.png`}
        alt={selected()[0]}
        height={30}
        width={30}
        class="rounded-sm"
      />
      <span class="tabular-nums">{selected()[1]}</span>
    </span>
  );
};

export const BuildingList: Component<{
  selectedBuildingsAccr: Accessor<string[]>;
  availableGoods: Accessor<string[]>;
}> = (props) => {
  const [options] = useOptionsContext();

  const buildings = Object.entries(recipesByBuilding);

  return (
    <Show when={options.showBuildingCards}>
      <div class="flex flex-wrap">
        <For each={buildings}>
          {([buildingName, recipes]) => (
            <Show when={props.selectedBuildingsAccr().includes(buildingName)}>
              <div class="bg-gray-100 p-4 m-4 rounded-lg flex flex-col items-center">
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
                    <h2 class="text-xl text-green-700">{buildingName}</h2>
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
                      const isFulfilled = () =>
                        ingredientSlots.every((slot) =>
                          Object.keys(slot).some((name) =>
                            props.availableGoods().includes(name)
                          )
                        );
                      return (
                        <li class="mb-1" classList={{ 'opacity-40': !isFulfilled() }}>
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
                                    <IngredientSlot slot={slot} availableGoods={props.availableGoods} />
                                    {slotIdx() < ingredientSlots.length - 1 && <span class="mx-1">+</span>}
                                  </>
                                )}
                              </For>
                              <span class="mx-1">=</span>
                              <span class="relative inline-flex">
                                <img
                                  src={`./icons/resources/60px-Icon_Resource_${makeResourceIconPart(productName)}.png`}
                                  alt={productName}
                                  height={36}
                                  width={36}
                                  class="rounded-sm shadow-lg"
                                />
                                <Show when={options.showRecipeNumber}>
                                  <span class="absolute bottom-0 right-0 text-xs tabular-nums font-bold text-white leading-none px-0.5" style="background: rgba(0,0,0,0.5);">{amount}</span>
                                </Show>
                              </span>
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
    </Show>
  );
};
