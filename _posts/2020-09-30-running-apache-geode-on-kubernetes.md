---
layout: post
category: blog
tags:
  - talks
  - geode
  - kubernetes
title: Running Apache Geode on Kubernetes
date: 2020-09-30
published: false
---

I had the opportunity to co-present at [ApacheCon @Home 2020](https://apachecon.com/acah2020/) with fellow Apache Geode committer [Michael Oleske](https://oleske.engineer/). Giving a talk at an all-virtual conference introduced some new challenges, but it was great that so many folks had free access because of the virtual format!

The abstract from our talk is below:

> As application developers move workloads to Kubernetes, they expect data services to run on Kubernetes alongside their applications. Kubernetes excels at running stateless workloads, but how does it handle complex stateful applications such as Apache Geode, a distributed in-memory database? We will describe challenges faced while building a Geode operator for Kubernetes, including controlling pod terminations, working with a dynamic network, and ensuring state management during the lifecycle of the deployment. We will explain the solutions we took to control these challenges, and dive into how we tested these solutions. You will leave with an understanding of how we moved a system designed to run on bare metal to a Kubernetes environment, uniting your workloads with your data services.

<div class="embedded-media">
  <iframe src="https://www.youtube-nocookie.com/embed/iNSObr15E9o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>
