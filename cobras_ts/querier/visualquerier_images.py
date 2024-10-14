import json
import os
import signal
import sys
import threading
from datetime import datetime

from .querier import Querier

from tornado import gen
from bokeh.layouts import row, column
from bokeh.models import Button, Toggle
from bokeh.models.widgets import Div

from functools import partial
import time
import random

colors = ["#cc6600", "#a0a0a0", "#00cccc", "#0066cc", "#0000cc"]


@gen.coroutine
def update(bokeh_layout, q1, q2, iteration, num_queries, fns, button_ml, button_cl):
    topdiv = Div(
        text="<img width=512 height=100 src=\'webapp_images/static/cobras_logo.png\'> <br><font size=\"2\"> <h3> # queries answered:  " + str(
            num_queries) + " </h3> </font>", css_classes=['top_title_div'],
        width=500, height=160)
    bokeh_layout.children[0] = topdiv




    q1 = Div(text="<img width=150 height=150 src='webapp_images/static/to_cluster/" + fns[q1].split('/')[-1] + "'>")
    q2 = Div(text="<img width=150 height=150 src='webapp_images/static/to_cluster/" + fns[q2].split('/')[-1] + "'>")

    div2 = Div(text="<h2> 这两张图片的内容是否属于同一个聚类？ </h2>", css_classes=['title_div'],
               width=500, height=60, name='wopwopwop')

    bokeh_layout.children[1] = div2

    bokeh_layout.children[2] = row(q1, q2)

    bokeh_layout.children[3] = column(button_ml, button_cl)


def cluster_is_pure(metadata, attr, old_value, new_value):
    metadata["cluster"].is_pure = not metadata["cluster"].is_pure


def cluster_is_finished(metadata, attr, old_value, new_value):
    metadata["cluster"].is_finished = not metadata["cluster"].is_finished


@gen.coroutine
def remove_cluster_indicators(querier, bokeh_layout):
    length = len(bokeh_layout.children)
    print("\n\n")
    print('are we in remove_cluster_indicators??')

    bokeh_layout.children[2] = row()
    for col in bokeh_layout.children[1].children:

        col.children[1] = row()
        col.children[2] = row()

    querier.finished_indicating = True

@gen.coroutine
def cluster_finished_indicator(querier, bokeh_layout):
    print('finish cluster')


    bokeh_layout.children[2] = row()
    bokeh_layout.children[3] = row()

    finished_div = Div(text="<h1> 聚类结果已完成 </h1>", css_classes=['title_div'], width=800, height=160)
    bokeh_layout.children[3] = finished_div

    querier.finished_indicating = True
    querier.finished_cluster = True
    print(querier)


def save_clustering_results(clusters, queries):

    name = sys.argv[5].split(" ")[3].split("\\")[-1]

    with open(name + "-" + str(queries) + "-end.txt", "w") as file:
        for cluster_id, cluster in enumerate(clusters):
            for member_id in cluster:

                file.write(f"{member_id} {cluster_id}\n")


def save_temp_clustering_results(clusters, queries):


    name = sys.argv[5].split(" ")[3].split("\\")[-1]  # objectCategories

    if not os.path.exists("results/" + name):
        os.makedirs("results/" + name)

    with open("results/" + name + "/" + name + "-" + str(queries) + ".txt", "w") as file:
        for cluster_id, cluster in enumerate(clusters):
            for member_id in cluster:

                file.write(f"{member_id} {cluster_id}\n")


def wait_for_finish_and_stop(querier):
    while not querier.finished_cluster:
        time.sleep(1)

    os.kill(os.getppid(), signal.SIGTERM)


def remove_cluster_indicators_callback(querier, bokeh_layout, bokeh_doc, clustering=None, cluster_indices=None,
                                       queries=0):
    print("\n\n\n\n\n")

    all_clusters_ok = all(cluster.is_pure or cluster.is_finished for cluster in clustering)
    if all_clusters_ok:

        print("所有聚类都是纯净的，保存结果并结束聚类。")
        save_clustering_results(cluster_indices, queries)

        bokeh_doc.add_next_tick_callback(
            partial(cluster_finished_indicator, querier=querier, bokeh_layout=bokeh_layout))

        wait_thread = threading.Thread(target=wait_for_finish_and_stop, args=(querier,))
        wait_thread.start()

    else:
        print("do we get in this callback?????")
        bokeh_doc.add_next_tick_callback(partial(remove_cluster_indicators, querier=querier, bokeh_layout=bokeh_layout))

        save_temp_clustering_results(cluster_indices, queries)


@gen.coroutine
def update_clustering(querier, bokeh_layout, bokeh_doc, data, clustering, cluster_indices, representatives, fns,
                      queries):
    plot_width = int(800 / len(clustering))
    plot_height = int(plot_width / 2)

    plots = []
    cols = []


    ctr = 0
    print('cluster_indices', cluster_indices)
    for c, c_idxs, cluster_representatives in zip(clustering, cluster_indices, representatives):

        print("\n\n\n")
        print('类簇包含的元素个数：', len(c_idxs))
        print('元素坐标：', c_idxs)

        n_to_plot = min(100, len(c_idxs))

        random_selection = random.sample(c_idxs, n_to_plot)

        table_str = "<div class=\"results\"><h3>Cluster " + str(ctr + 1) + " - 目前包含" + str(
            len(c_idxs)) + "个元素</h3><table><tr> "
        for i in range(n_to_plot):
            table_str += "<td><img width=65 height=65 src='webapp_images/static/to_cluster/" + \
                         fns[random_selection[i]].split('/')[-1] + "'></td>"
            if (i + 1) % 5 == 0:
                table_str += "</tr><tr>"

        table_str += "</tr></table></div>"

        if ctr % 2 == 0:
            table_str += "<br/><br/>"

        ctr += 1

        test_div = Div(text=table_str, width=500)

        button = Toggle(label="该类别是纯类别！！", active=c.is_pure)
        button.on_change("active", partial(cluster_is_pure, {"cluster": c}))

        button2 = Toggle(label="该类别是纯类别并且已经聚类完成！！", active=c.is_finished)
        button2.on_change("active", partial(cluster_is_finished, {"cluster": c}))

        cols.append(column(test_div, button, button2))

    topdiv = Div(
        text="<img width=512 height=100 src=\'webapp_images/static/cobras_logo.png\'> <br><font size=\"2\"> </font>",
        css_classes=['top_title_div'],
        width=500, height=120)
    bokeh_layout.children[0] = topdiv

    bokeh_layout.children[1] = row(cols)

    finished_indicating = Button(label="展示更多的聚类选项", button_type="danger")
    finished_indicating.on_click(
        partial(remove_cluster_indicators_callback, querier=querier, bokeh_layout=bokeh_layout, bokeh_doc=bokeh_doc,
                clustering=clustering, cluster_indices=cluster_indices, queries=queries))

    bokeh_layout.children[2] = row(finished_indicating)

    bokeh_layout.children[3] = Div(text="")


class VisualImageQuerier(Querier):

    def __init__(self, data, bokeh_doc, bokeh_layout, fns, button_ml, button_cl):
        super(VisualImageQuerier, self).__init__()

        self.data = data
        self.fns = fns

        self.bokeh_doc = bokeh_doc
        self.bokeh_layout = bokeh_layout

        self.query_answered = False
        self.query_result = None

        self.iteration = 0
        self.n_queries = 0

        self.finished_indicating = False

        self.button_ml = button_ml
        self.button_cl = button_cl

    def query_points(self, idx1, idx2):

        time.sleep(0.8)

        self.bokeh_doc.add_next_tick_callback(
            partial(update, bokeh_layout=self.bokeh_layout, q1=idx1, q2=idx2, iteration=self.iteration,
                    num_queries=self.n_queries, fns=self.fns, button_ml=self.button_ml, button_cl=self.button_cl))

        while not self.query_answered:
            pass

        self.query_answered = False

        self.n_queries += 1

        return self.query_result

    def finished_indicating(self):
        return self.finished_indicating

    def update_clustering(self, clustering):

        self.finished_indicating = False


        clusters = []
        cluster_indices = []
        si_representatives = []
        for cluster in clustering.clusters:
            clusters.append(cluster)
            cluster_indices.append(cluster.get_all_points())
            si_representatives.append([si.representative_idx for si in cluster.super_instances])

        time.sleep(0.8)


        self.bokeh_doc.add_next_tick_callback(
            partial(update_clustering, querier=self, bokeh_layout=self.bokeh_layout, bokeh_doc=self.bokeh_doc,
                    data=self.data, clustering=clusters, cluster_indices=cluster_indices,
                    representatives=si_representatives, fns=self.fns, queries=self.n_queries))

        while not self.finished_indicating:

            pass

        self.iteration += 1
