from configuration import TRUE_REWARDS, FEATURES
import pandas as pd

import matplotlib.pylab as plt
import seaborn as sns


def visualize_pragmatic_beliefs(belief_df, vmax=.5, cmap='Oranges'):
    """Belief DF should have a prob column indicating the probability of each world."""

    value_probs = []
    for k in TRUE_REWARDS.keys():
        for v, g in belief_df.groupby(k):
            value_probs.append({"feature": k, "value": v, "prob": g.probability.sum()})

    prob_df = pd.DataFrame(value_probs)
    visualize_utt_distribution(prob_df, vmax=vmax, cmap=cmap)


def visualize_utt_distribution(prob_df, vmax=.5, cmap='Oranges'):
    collapsed_probs = prob_df.pivot("value", "feature", "prob")

    features_in_descending_order = ["green", "circle", "red", "triangle", "square", "blue"]
    reward_probs = collapsed_probs.reindex(features_in_descending_order, axis=1)

    ax = sns.heatmap(reward_probs, fmt='', linewidths=.5, cmap=cmap, vmin=0, vmax=vmax)
    ax.invert_yaxis()


def plot_horizon_estimate(posterior_df, include_text=True, include_ticks=True):
    plt.figure(figsize=(12, 2))
    posterior_df.groupby('horizon').probability.sum().plot(kind='bar', color='gray', alpha=1, rot=0, fontsize=20)

    plt.xlabel("Speaker Horizon $H$", fontsize=25)

    ys = [.2, .4, .6]
    plt.xticks(fontsize=25)
    for y in ys:
        plt.axhline(y, alpha=.5, linestyle='--', c='k', zorder=0)
    if include_ticks:
        plt.yticks(ys, fontsize=25)
    else:
        plt.yticks(ys, fontsize=0)
    if include_text:
        plt.ylabel("Posterior \nProbability", fontsize=25)
    plt.ylim(0, .65)


def plot_point_estimate(point_estimate, color='gray', alpha=1, include_text=True):
    plt.figure(figsize=(8, 4))

    point_estimate = point_estimate[["green", "red", "blue", "circle", "triangle", "square"]]

    point_estimate.plot(kind='bar', color=color, alpha=alpha)

    ys = [-1, -.5, 0, .5, 1]
    for y in ys:
        plt.axhline(y, alpha=.5, linestyle='--', color='k', zorder=0)
    plt.yticks([-1, 0, 1], size=25)

    if include_text:
        plt.ylabel("Posterior Mean Rewards", fontsize=22)

    plt.axhline(0, color='k')
    plt.ylim(-1.5, 1.5)


def plot_full_posterior(description_posterior, ylabel):
    fig, axes = plt.subplots(6, 1, figsize=(8, 6))

    for i, (f, ax) in enumerate(zip(FEATURES, axes)):
        posterior = description_posterior.groupby(f)["probability"].sum().reset_index()

        sns.barplot(data=posterior, x=f, y='probability', ax=ax, palette=['k'])
        ax.set_xlabel("")
        ax.set_ylim(0, .8)
        ax.axhline(.2, linestyle='--', c='gray', zorder=0)

        if ylabel:
            ax.set_ylabel(f)
            ax.set_yticks([0, .2, .4, .6])
            ax.tick_params(axis='y', which='major', labelsize=10)

        else:
            ax.set_ylabel("")
            ax.set_yticks([0, .2, .4, .6])
            ax.tick_params(axis='y', which='major', labelsize=0)

        ax.tick_params(axis='x', which='major', labelsize=20)
        if i != 5:
            ax.set_xticks([])